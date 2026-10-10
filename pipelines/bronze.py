"""Bronze: land each raw parquet file as-is (plus metadata) into a Delta table.

Local stand-in for Databricks Auto Loader (cloudFiles). Idempotent: a file already present in
bronze (by _source_file) is skipped. New columns evolve the schema (mergeSchema); a changed
column *type* is NOT absorbed and fails the append, as it would in production.
"""
import glob
import os

from delta.tables import DeltaTable
from pyspark.sql import functions as F

from pipelines.common.spark import BRONZE_PATH, RAW_DIR, get_spark
from pipelines.transforms import to_bronze


def already_ingested(spark) -> set:
    if not DeltaTable.isDeltaTable(spark, BRONZE_PATH):
        return set()
    rows = spark.read.format("delta").load(BRONZE_PATH).select("_source_file").distinct().collect()
    return {r["_source_file"] for r in rows}


def run(spark=None) -> int:
    spark = spark or get_spark("bronze")
    files = sorted(glob.glob(os.path.join(RAW_DIR, "yellow", "*.parquet")))
    if not files:
        raise FileNotFoundError(f"No parquet files in {RAW_DIR}/yellow. Run scripts/download_taxi_data.py")
    done = already_ingested(spark)
    new = 0
    for path in files:
        name = os.path.basename(path)
        if name in done:
            print(f"[bronze] skip {name} (already ingested)")
            continue
        df = to_bronze(spark.read.parquet(path), name)
        (
            df.write.format("delta")
            .mode("append")
            .option("mergeSchema", "true")
            .save(BRONZE_PATH)
        )
        print(f"[bronze] ingested {name}")
        new += 1
    total = spark.read.format("delta").load(BRONZE_PATH).count()
    print(f"[bronze] done: {new} new file(s), {total:,} rows in bronze")
    return total


if __name__ == "__main__":
    run()
