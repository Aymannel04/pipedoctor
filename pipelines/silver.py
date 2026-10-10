"""Silver: typed, de-duplicated trips. Invalid rows go to a quarantine table.

* Idempotent: rows are MERGEd on trip_id, so re-running never creates duplicates.
* Delta CHECK constraints guard the table; they hold because invalid rows are quarantined first.
"""
from delta.tables import DeltaTable

from pipelines.common.spark import BRONZE_PATH, QUARANTINE_PATH, SILVER_PATH, get_spark
from pipelines.transforms import split_valid, to_silver_candidates

CONSTRAINTS = {
    "fare_non_negative": "fare_amount >= 0",
    "distance_non_negative": "trip_distance >= 0",
    "pickup_before_dropoff": "pickup_ts <= dropoff_ts",
}


def ensure_constraints(spark) -> None:
    for name, expr in CONSTRAINTS.items():
        try:
            spark.sql(f"ALTER TABLE delta.`{SILVER_PATH}` ADD CONSTRAINT {name} CHECK ({expr})")
        except Exception as exc:  # already exists on re-runs
            if "already exists" not in str(exc).lower():
                raise


def run(spark=None) -> dict:
    spark = spark or get_spark("silver")
    bronze = spark.read.format("delta").load(BRONZE_PATH)
    valid, quarantined = split_valid(to_silver_candidates(bronze))

    if DeltaTable.isDeltaTable(spark, SILVER_PATH):
        (
            DeltaTable.forPath(spark, SILVER_PATH)
            .alias("t")
            .merge(valid.alias("s"), "t.trip_id = s.trip_id")
            .whenNotMatchedInsertAll()
            .execute()
        )
    else:
        valid.write.format("delta").partitionBy("pickup_date").save(SILVER_PATH)
    ensure_constraints(spark)

    quarantined.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(QUARANTINE_PATH)

    stats = {
        "silver": spark.read.format("delta").load(SILVER_PATH).count(),
        "quarantine": spark.read.format("delta").load(QUARANTINE_PATH).count(),
    }
    print(f"[silver] done: {stats['silver']:,} trips, {stats['quarantine']:,} quarantined")
    return stats


if __name__ == "__main__":
    run()
