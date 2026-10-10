"""Download NYC TLC yellow-taxi monthly parquet files into RAW_DIR (default /data/raw/yellow).

    python scripts/download_taxi_data.py --start 2024-01 --months 3
"""
import argparse
import os
import sys
import urllib.request

BASE = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{ym}.parquet"


def month_range(start: str, n: int):
    y, m = map(int, start.split("-"))
    for _ in range(n):
        yield f"{y:04d}-{m:02d}"
        m += 1
        if m == 13:
            y, m = y + 1, 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2024-01", help="first month, YYYY-MM")
    ap.add_argument("--months", type=int, default=3)
    ap.add_argument("--out", default=os.path.join(os.getenv("RAW_DIR", "/data/raw"), "yellow"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for ym in month_range(a.start, a.months):
        dest = os.path.join(a.out, f"yellow_tripdata_{ym}.parquet")
        if os.path.exists(dest):
            print(f"skip   {dest} (already there)")
            continue
        url = BASE.format(ym=ym)
        print(f"get    {url}")
        tmp = dest + ".part"
        urllib.request.urlretrieve(url, tmp)
        os.replace(tmp, dest)
        print(f"saved  {dest} ({os.path.getsize(dest) / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
