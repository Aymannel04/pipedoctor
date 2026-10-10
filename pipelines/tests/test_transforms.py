from datetime import datetime as dt

import pytest
from pyspark.sql import functions as F

from pipelines.transforms import (
    normalize_columns,
    split_valid,
    to_bronze,
    to_gold,
    to_silver_candidates,
)

FILE = "yellow_tripdata_2024-01.parquet"


def raw_rows(spark, rows):
    """Raw TLC-style frame (mixed-case names, like the real files)."""
    cols = [
        "VendorID", "tpep_pickup_datetime", "tpep_dropoff_datetime", "passenger_count",
        "trip_distance", "RatecodeID", "store_and_fwd_flag", "PULocationID", "DOLocationID",
        "payment_type", "fare_amount", "extra", "mta_tax", "tip_amount", "tolls_amount",
        "improvement_surcharge", "total_amount", "congestion_surcharge", "Airport_fee",
    ]
    return spark.createDataFrame(rows, cols)


def good(pickup=dt(2024, 1, 5, 10, 0), dropoff=dt(2024, 1, 5, 10, 20), pu=100, do=200, fare=15.0, total=20.0, dist=3.2):
    return (1, pickup, dropoff, 1.0, dist, 1.0, "N", pu, do, 1, fare, 0.5, 0.5, 2.0, 0.0, 1.0, total, 2.5, 0.0)


def silver_of(spark, rows):
    return to_silver_candidates(to_bronze(raw_rows(spark, rows), FILE))


def test_normalize_columns_lowercases(spark):
    df = normalize_columns(raw_rows(spark, [good()]))
    assert "pulocationid" in df.columns and "airport_fee" in df.columns
    assert "PULocationID" not in df.columns


def test_bronze_applies_contract_types(spark):
    df = to_bronze(raw_rows(spark, [good()]), FILE)
    types = dict(df.dtypes)
    assert types["passenger_count"] == "bigint"  # was double in the raw frame
    assert types["tpep_pickup_datetime"] == "timestamp"
    assert "_source_file" in types and "_ingested_at" in types


def test_silver_renames_and_derives(spark):
    row = silver_of(spark, [good()]).collect()[0]
    assert row["pu_location_id"] == 100 and row["do_location_id"] == 200
    assert row["trip_duration_min"] == pytest.approx(20.0)
    assert str(row["pickup_date"]) == "2024-01-05"
    assert len(row["trip_id"]) == 64


def test_silver_missing_optional_column_is_null(spark):
    df = raw_rows(spark, [good()]).drop("Airport_fee")
    out = to_silver_candidates(to_bronze(df, FILE)).collect()[0]
    assert out["airport_fee"] is None and out["cbd_congestion_fee"] is None


def test_silver_missing_required_column_fails_loudly(spark):
    from pyspark.errors import AnalysisException

    df = raw_rows(spark, [good()]).withColumnRenamed("fare_amount", "fare_amt")
    with pytest.raises(AnalysisException):
        to_silver_candidates(to_bronze(df, FILE)).collect()


def test_split_quarantines_each_invalid_rule(spark):
    rows = [
        good(),                                                        # valid
        good(fare=-5.0, total=-5.0),                                   # negative fare
        good(pickup=dt(2024, 1, 5, 11, 0), dropoff=dt(2024, 1, 5, 10, 0)),  # pickup after dropoff
        good(pickup=dt(2002, 12, 31, 1, 0), dropoff=dt(2002, 12, 31, 2, 0)),  # outside file month
        good(pu=None),                                                 # null location
        good(dist=-1.0),                                               # negative distance
    ]
    valid, quarantined = split_valid(silver_of(spark, rows))
    reasons = {r["quarantine_reason"] for r in quarantined.collect()}
    assert valid.count() == 1
    assert reasons == {
        "negative_or_null_fare", "pickup_after_dropoff", "pickup_outside_file_month",
        "null_location", "negative_or_null_distance",
    }


def test_duplicates_collapse_on_trip_id(spark):
    valid, _ = split_valid(silver_of(spark, [good(), good(), good(fare=16.0, total=21.0)]))
    assert valid.count() == 2


def test_gold_aggregates_per_day_and_zone(spark):
    rows = [good(total=20.0, dist=2.0), good(total=30.0, dist=4.0), good(pu=101, total=10.0, dist=1.0)]
    valid, _ = split_valid(silver_of(spark, rows))
    gold = {(str(r["pickup_date"]), r["pu_location_id"]): r for r in to_gold(valid).collect()}
    r = gold[("2024-01-05", 100)]
    assert r["trips"] == 2 and r["revenue"] == 50.0 and r["avg_distance"] == 3.0
    assert gold[("2024-01-05", 101)]["trips"] == 1
