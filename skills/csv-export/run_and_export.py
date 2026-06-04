#!/usr/bin/env python3
"""Run Immoweb Apify actor and export results to CSV on Railway volume."""

import json
import os
import sys
from apify_client import ApifyClient
from append_csv import append_items

ACTOR_ID = "UUjIYNdzU5Mo8szQN"  # Immoweb Belgian Real Estate Scraper
APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "")


def run_and_export(input_params: dict) -> int:
    if not APIFY_TOKEN:
        print("ERROR: APIFY_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    client = ApifyClient(APIFY_TOKEN)
    print(f"Starting Immoweb actor {ACTOR_ID} ...")
    run = client.actor(ACTOR_ID).call(run_input=input_params)
    dataset_id = run["defaultDatasetId"]
    print(f"Run finished. Dataset: {dataset_id}")

    items = list(client.dataset(dataset_id).iterate_items())
    print(f"Fetched {len(items)} items from dataset.")

    return append_items(items)


if __name__ == "__main__":
    params = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    run_and_export(params)
