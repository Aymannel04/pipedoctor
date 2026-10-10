# Local replica of the Databricks lakehouse: PySpark + Delta Lake. Free to run.
FROM python:3.11-slim-bookworm

RUN apt-get update \
 && apt-get install -y --no-install-recommends openjdk-17-jre-headless procps \
 && rm -rf /var/lib/apt/lists/*

COPY docker/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Pre-fetch the Delta jars at build time so runs do not need internet for them.
RUN python -c "\
from delta import configure_spark_with_delta_pip as c; \
from pyspark.sql import SparkSession as S; \
b = (S.builder.master('local[1]') \
     .config('spark.sql.extensions','io.delta.sql.DeltaSparkSessionExtension') \
     .config('spark.sql.catalog.spark_catalog','org.apache.spark.sql.delta.catalog.DeltaCatalog')); \
s = c(b).getOrCreate(); s.range(1).write.format('delta').save('/tmp/warmup'); s.stop()"

WORKDIR /workspace
ENV PYTHONPATH=/workspace \
    PYTHONUNBUFFERED=1 \
    LAKEHOUSE_DIR=/data/lakehouse \
    RAW_DIR=/data/raw
