# Guide 02: code walkthrough (Step 2)

*How to read the code I wrote for the local lakehouse, file by file, in the order that makes sense.*

## Open it in VS Code
```powershell
cd C:\dev\pipedoctor      # or wherever the folder is
code .
```
Useful extensions: **Python** (Microsoft), **Docker**. VS Code is only for reading and editing; the pipeline runs inside Docker, not in VS Code.

## Reading order
| # | File | One line |
|---|---|---|
| 1 | `pipelines/common/spark.py` | Starts Spark and defines where each table lives |
| 2 | `pipelines/transforms.py` | All the cleaning logic, as pure functions (the heart) |
| 3 | `pipelines/bronze.py` | Loads raw files into the bronze table |
| 4 | `pipelines/silver.py` | Cleans bronze into silver; bad rows to quarantine |
| 5 | `pipelines/gold.py` | Summarises silver per day and zone |
| 6 | `pipelines/run_all.py` | Runs the three layers in order |
| 7 | `pipelines/tests/` | Checks the logic on tiny fake data |
| 8 | `docker/`, `docker-compose.yml`, `scripts/download_taxi_data.py` | The environment and the data download |

## 1. `common/spark.py`
- `get_spark()` creates the Spark engine on your machine (`local[*]` = use all CPU cores) and, when `delta=True`, switches on Delta Lake.
- Constants like `BRONZE_PATH`, `SILVER_PATH` say where each table is stored under `data/lakehouse`.
- Why: one place to change settings, and tests can ask for plain Spark without Delta.

## 2. `transforms.py` (read this one most carefully)
Everything here takes a table in and returns a table out. No files, no Delta. Parts:
- **`BRONZE_CONTRACT`**: a dictionary "column name -> type" (e.g. `fare_amount: double`). It forces known columns to a stable type.
- **`normalize_columns`**: lower-cases column names, because the taxi files mix `Airport_fee` and `airport_fee`.
- **`to_bronze`**: normalise, apply the contract, add `_source_file` and `_ingested_at`.
- **`to_silver_candidates`**: renames columns (`tpep_pickup_datetime` -> `pickup_ts`), picks the needed ones, computes `trip_duration_min`, and builds `trip_id` (a SHA-256 fingerprint of the trip's key fields).
- **`quarantine_reason`**: the validity rules, as a first-match-wins list: null timestamps, null locations, pickup after dropoff, pickup outside the file's month, negative fare/total/distance. A row that passes gets `NULL`.
- **`split_valid`**: splits into `valid` (de-duplicated by `trip_id`) and `quarantined`.
- **`to_gold`**: groups by day and pickup zone: trips, revenue, average distance, average tip.

## 3. `bronze.py`
Loop over the parquet files in `data/raw/yellow/`. For each file not already in bronze: read it, run `to_bronze`, append to the Delta table with `mergeSchema=true` (new columns are allowed; a changed column *type* is not and will fail). Re-running skips files already loaded.

## 4. `silver.py`
1. Read bronze, run `to_silver_candidates` then `split_valid`.
2. If the silver table exists, **MERGE** on `trip_id` (insert only the trips not already there); otherwise create it, partitioned by `pickup_date`.
3. `ensure_constraints`: add Delta CHECK rules (`fare_amount >= 0`, `trip_distance >= 0`, `pickup_ts <= dropoff_ts`) so bad data can never be written even by mistake.
4. Write the quarantined rows to their own table (overwritten each run).

## 5. `gold.py`
Read silver, call `to_gold`, overwrite the gold table.

## 6. `run_all.py`
Creates one Spark session and calls `bronze.run`, `silver.run`, `gold.run`, then prints how long it took.

## 7. Tests
`tests/test_transforms.py` builds a handful of fake trips (one good, several with a specific defect) and checks each rule: renaming, types, each quarantine reason, duplicates collapsing, gold totals. `conftest.py` provides the shared Spark session.

## 8. Environment
- `docker/Dockerfile`: the recipe for the container (Java, Python, PySpark, Delta).
- `docker-compose.yml`: mounts your project at `/workspace` and `data/` at `/data` so files persist.
- `download_taxi_data.py`: downloads the monthly parquet files.

## Where PipeDoctor will break things later
| Code | Failure scenario that will target it |
|---|---|
| `BRONZE_CONTRACT`, `mergeSchema` | 1 schema drift, 2 type change |
| `quarantine_reason`, CHECK constraints | 3 invalid values |
| MERGE on `trip_id` | 8 duplicates after a retry |
| required column names in `to_silver_candidates` | 11 column removed upstream |
