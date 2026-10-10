# Pipelines (local lakehouse)

Medallion pipeline on NYC yellow-taxi data, run locally in Docker (PySpark + Delta Lake).

| Layer | Path (under `data/lakehouse`) | What it holds |
|---|---|---|
| bronze | `bronze/yellow_trips` | Raw rows, lower-case columns, stable types, `_source_file`, `_ingested_at` |
| silver | `silver/trips` | Typed, de-duplicated trips; MERGE on `trip_id`; Delta CHECK constraints |
| quarantine | `silver/trips_quarantine` | Invalid rows with a `quarantine_reason` |
| gold | `gold/daily_zone_revenue` | Trips and revenue per pickup day and zone |

## Run it
```powershell
docker compose build
docker compose run --rm lakehouse python scripts/download_taxi_data.py --start 2024-01 --months 3
docker compose run --rm lakehouse python -m pytest pipelines/tests -q
docker compose run --rm lakehouse python -m pipelines.run_all
```
Start over: delete the `data/lakehouse` folder.

## Why it is built this way
- `pipelines/transforms.py` holds pure functions, so the logic is unit-tested without Delta.
- Silver is idempotent (MERGE) and guarded by CHECK constraints; invalid rows are quarantined first.
  Failure scenarios #3 (invalid values), #8 (duplicates after retry) and #9 (concurrent writes)
  will break exactly these pieces.
- `bronze.py` is the local stand-in for Databricks Auto Loader (`cloudFiles`); the Azure version
  swaps only the read.
