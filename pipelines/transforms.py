"""Pure DataFrame -> DataFrame transformations. No Delta, no I/O, so they are easy to test.

Layers:
  bronze: raw files as received (lower-case column names, stable types, ingestion metadata)
  silver: clean, typed, de-duplicated trips; invalid rows are quarantined with a reason
  gold:   daily revenue per pickup zone
"""
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

# --- bronze landing contract: lower-case raw column name -> type -------------------------
# Unknown columns pass through untouched (Delta schema evolution adds them).
BRONZE_CONTRACT = {
    "vendorid": "bigint",
    "tpep_pickup_datetime": "timestamp",
    "tpep_dropoff_datetime": "timestamp",
    "passenger_count": "bigint",
    "trip_distance": "double",
    "ratecodeid": "bigint",
    "store_and_fwd_flag": "string",
    "pulocationid": "bigint",
    "dolocationid": "bigint",
    "payment_type": "bigint",
    "fare_amount": "double",
    "extra": "double",
    "mta_tax": "double",
    "tip_amount": "double",
    "tolls_amount": "double",
    "improvement_surcharge": "double",
    "total_amount": "double",
    "congestion_surcharge": "double",
    "airport_fee": "double",
    "cbd_congestion_fee": "double",
}

# --- bronze -> silver column names -----------------------------------------------------
RENAMES = {
    "vendorid": "vendor_id",
    "tpep_pickup_datetime": "pickup_ts",
    "tpep_dropoff_datetime": "dropoff_ts",
    "ratecodeid": "rate_code_id",
    "pulocationid": "pu_location_id",
    "dolocationid": "do_location_id",
}

OPTIONAL_DOUBLE = ["congestion_surcharge", "airport_fee", "cbd_congestion_fee"]


def normalize_columns(df: DataFrame) -> DataFrame:
    """Lower-case every column name (the TLC files mix e.g. Airport_fee / airport_fee)."""
    return df.toDF(*[c.lower() for c in df.columns])


def apply_bronze_contract(df: DataFrame) -> DataFrame:
    for name, dtype in BRONZE_CONTRACT.items():
        if name in df.columns:
            df = df.withColumn(name, F.col(name).cast(dtype))
    return df


def to_bronze(df: DataFrame, source_file: str) -> DataFrame:
    df = apply_bronze_contract(normalize_columns(df))
    return df.withColumn("_source_file", F.lit(source_file)).withColumn(
        "_ingested_at", F.current_timestamp()
    )


def _opt(df: DataFrame, name: str, dtype: str):
    """A column that may be absent from older/newer files: null when missing."""
    return (F.col(name) if name in df.columns else F.lit(None)).cast(dtype).alias(name)


def to_silver_candidates(bronze: DataFrame) -> DataFrame:
    """Rename, select and derive. Required columns are referenced directly, so a missing
    one fails loudly with a Spark AnalysisException."""
    df = bronze
    for old, new in RENAMES.items():
        if old in df.columns:
            df = df.withColumnRenamed(old, new)

    cols = [
        F.col("vendor_id"),
        F.col("pickup_ts"),
        F.col("dropoff_ts"),
        F.to_date("pickup_ts").alias("pickup_date"),
        F.col("passenger_count"),
        F.col("trip_distance"),
        F.col("rate_code_id"),
        F.col("store_and_fwd_flag"),
        F.col("pu_location_id"),
        F.col("do_location_id"),
        F.col("payment_type"),
        F.col("fare_amount"),
        F.col("extra"),
        F.col("mta_tax"),
        F.col("tip_amount"),
        F.col("tolls_amount"),
        F.col("improvement_surcharge"),
        F.col("total_amount"),
        *[_opt(df, c, "double") for c in OPTIONAL_DOUBLE],
        F.round(
            (F.col("dropoff_ts").cast("long") - F.col("pickup_ts").cast("long")) / 60.0, 2
        ).alias("trip_duration_min"),
        F.col("_source_file"),
    ]
    out = df.select(*cols)
    return out.withColumn(
        "trip_id",
        F.sha2(
            F.concat_ws(
                "|",
                F.col("vendor_id").cast("string"),
                F.col("pickup_ts").cast("string"),
                F.col("dropoff_ts").cast("string"),
                F.col("pu_location_id").cast("string"),
                F.col("do_location_id").cast("string"),
                F.col("trip_distance").cast("string"),
                F.col("fare_amount").cast("string"),
                F.col("total_amount").cast("string"),
            ),
            256,
        ),
    )


def quarantine_reason():
    """First failing rule wins; NULL means the row is valid."""
    file_month = F.regexp_extract(F.col("_source_file"), r"(\d{4}-\d{2})", 1)
    return (
        F.when(F.col("pickup_ts").isNull() | F.col("dropoff_ts").isNull(), "null_timestamp")
        .when(F.col("pu_location_id").isNull() | F.col("do_location_id").isNull(), "null_location")
        .when(F.col("pickup_ts") > F.col("dropoff_ts"), "pickup_after_dropoff")
        .when(F.date_format("pickup_ts", "yyyy-MM") != file_month, "pickup_outside_file_month")
        .when(F.col("fare_amount").isNull() | (F.col("fare_amount") < 0), "negative_or_null_fare")
        .when(F.col("total_amount").isNull() | (F.col("total_amount") < 0), "negative_or_null_total")
        .when(F.col("trip_distance").isNull() | (F.col("trip_distance") < 0), "negative_or_null_distance")
    )


def split_valid(candidates: DataFrame):
    """Return (valid, quarantined). Valid rows are de-duplicated on trip_id."""
    flagged = candidates.withColumn("quarantine_reason", quarantine_reason())
    valid = (
        flagged.filter(F.col("quarantine_reason").isNull())
        .drop("quarantine_reason")
        .dropDuplicates(["trip_id"])
    )
    quarantined = flagged.filter(F.col("quarantine_reason").isNotNull())
    return valid, quarantined


def to_gold(silver: DataFrame) -> DataFrame:
    return silver.groupBy("pickup_date", "pu_location_id").agg(
        F.count("*").alias("trips"),
        F.round(F.sum("total_amount"), 2).alias("revenue"),
        F.round(F.avg("trip_distance"), 3).alias("avg_distance"),
        F.round(F.avg("tip_amount"), 3).alias("avg_tip"),
    )
