"""Gold: daily revenue per pickup zone, recomputed from silver on every run."""
from pipelines.common.spark import GOLD_PATH, SILVER_PATH, get_spark
from pipelines.transforms import to_gold


def run(spark=None) -> int:
    spark = spark or get_spark("gold")
    gold = to_gold(spark.read.format("delta").load(SILVER_PATH))
    gold.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(GOLD_PATH)
    n = spark.read.format("delta").load(GOLD_PATH).count()
    print(f"[gold] done: {n:,} rows")
    return n


if __name__ == "__main__":
    run()
