#!/usr/bin/env python3
"""Append Apify actor items to the persistent CSV on the Railway volume."""

import csv
import json
import os
import sys
from datetime import datetime, timezone

CSV_PATH = "/opt/data/apify_export.csv"


def append_items(items: list[dict]) -> int:
    if not items:
        print("No items to append.")
        return 0

    fieldnames = sorted({k for item in items for k in item.keys()})
    fieldnames = ["_scraped_at"] + fieldnames

    file_exists = os.path.exists(CSV_PATH)
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)

    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        ts = datetime.now(timezone.utc).isoformat()
        for item in items:
            writer.writerow({"_scraped_at": ts, **item})

    print(f"Appended {len(items)} rows to {CSV_PATH}")
    return len(items)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: append_csv.py '<json_array>'")
        sys.exit(1)
    data = json.loads(sys.argv[1])
    if isinstance(data, dict):
        data = [data]
    count = append_items(data)
    sys.exit(0 if count >= 0 else 1)
