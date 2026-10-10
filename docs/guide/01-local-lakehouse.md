# Guide 01: the local lakehouse

*Doc checkpoint 1 (covers Steps 1-2). Update this page when the pipeline changes.*

## What it is
A small lakehouse that runs on a laptop in Docker. It is the system PipeDoctor will watch: the
pipeline whose failures we inject and the agent diagnoses. It mirrors the Azure Databricks setup
(PySpark + Delta Lake) so the same code moves to Azure later.

## Data flow
```
data/raw/yellow/*.parquet          (NYC TLC yellow-taxi, one file per month)
        |  bronze.py   raw rows + stable types + _source_file + _ingested_at
        v
bronze/yellow_trips (Delta)
        |  silver.py   rename, derive, validate, de-duplicate, MERGE on trip_id
        v
silver/trips (Delta) ----> silver/trips_quarantine (Delta, invalid rows with a reason)
        |  gold.py     daily trips and revenue per pickup zone
        v
gold/daily_zone_revenue (Delta)
```
Everything lives under `data/lakehouse` (ignored by git).

## Code map
| File | Role |
|---|---|
| `pipelines/transforms.py` | Pure DataFrame functions; unit-tested without Delta |
| `pipelines/bronze.py` | Land each file once into Delta (stand-in for Auto Loader) |
| `pipelines/silver.py` | MERGE valid rows, quarantine invalid rows, ensure CHECK constraints |
| `pipelines/gold.py` | Aggregate silver |
| `pipelines/run_all.py` | bronze -> silver -> gold |
| `pipelines/common/spark.py` | SparkSession with Delta, and the table paths |
| `scripts/download_taxi_data.py` | Fetch monthly parquet files |
| `docker/`, `docker-compose.yml` | The runtime |

## How to run
```powershell
docker compose build
docker compose run --rm lakehouse python scripts/download_taxi_data.py --start 2024-01 --months 3
docker compose run --rm lakehouse python -m pytest pipelines/tests -q
docker compose run --rm lakehouse python -m pipelines.run_all
```
Start over by deleting `data/lakehouse`. A green run ends with `[run_all] green in ...s`.

## Design choices (and why they matter for the agent)
- **Pure transforms.** Logic is tested without Delta, so a failing test points at logic and a failing run at the platform.
- **Idempotent silver (MERGE on `trip_id`).** Re-running creates no duplicates. Scenario 8 (duplicates after a retry) breaks exactly this.
- **Delta CHECK constraints** (`fare_amount >= 0`, `trip_distance >= 0`, `pickup_ts <= dropoff_ts`) plus a quarantine step. Scenario 3 (invalid values) removes the quarantine and trips the constraint.
- **Bronze type contract.** Known columns are cast to stable types; unknown columns pass through and evolve the schema. Scenarios 1 and 2 (schema drift, type change) break this.
- **Required columns are referenced directly**, so a renamed column fails with a real Spark `AnalysisException`, the kind of error the agent has to read.

## Known limits
- Bronze is a batch stand-in for Auto Loader; the Azure version swaps only the read (`cloudFiles`).
- Silver reprocesses all of bronze each run; fine at this scale.
- Untested so far on the user's machine at the time of writing (see the journal).

## Troubleshooting
| Symptom | Likely cause | Fix |
|---|---|---|
| Docker build fails at the Delta warm-up step | No network to Maven during build | Retry on a normal connection |
| `Cannot connect to the Docker daemon` | Docker Desktop not running | Start it |
| Bind mount is empty or slow | Project inside OneDrive | Move to `C:\dev\pipedoctor` |
| Out-of-memory in Spark | Driver memory too low | Raise `SPARK_DRIVER_MEMORY` in `docker-compose.yml` |
