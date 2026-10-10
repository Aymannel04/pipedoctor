"""Run bronze -> silver -> gold. Usage:  python -m pipelines.run_all"""
import time

from pipelines import bronze, gold, silver
from pipelines.common.spark import get_spark


def main() -> None:
    spark = get_spark("pipedoctor-run-all")
    t0 = time.time()
    bronze.run(spark)
    silver.run(spark)
    gold.run(spark)
    print(f"[run_all] green in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
