import os

from pyspark.sql import SparkSession

LAKEHOUSE_DIR = os.getenv("LAKEHOUSE_DIR", "/data/lakehouse")
RAW_DIR = os.getenv("RAW_DIR", "/data/raw")

BRONZE_PATH = f"{LAKEHOUSE_DIR}/bronze/yellow_trips"
SILVER_PATH = f"{LAKEHOUSE_DIR}/silver/trips"
QUARANTINE_PATH = f"{LAKEHOUSE_DIR}/silver/trips_quarantine"
GOLD_PATH = f"{LAKEHOUSE_DIR}/gold/daily_zone_revenue"


def get_spark(app_name: str = "pipedoctor", delta: bool = True) -> SparkSession:
    """Local SparkSession. delta=False gives plain Spark (used by unit tests)."""
    builder = (
        SparkSession.builder.appName(app_name)
        .master("local[*]")
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.shuffle.partitions", os.getenv("SHUFFLE_PARTITIONS", "8"))
        .config("spark.driver.memory", os.getenv("SPARK_DRIVER_MEMORY", "4g"))
        .config("spark.ui.showConsoleProgress", "false")
    )
    if delta:
        from delta import configure_spark_with_delta_pip

        builder = builder.config(
            "spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension"
        ).config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
        return configure_spark_with_delta_pip(builder).getOrCreate()
    return builder.getOrCreate()
