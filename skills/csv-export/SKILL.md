# CSV Export Skill

Export Apify actor results to a persistent CSV file on the Railway volume.

## Usage

Call this skill after any Apify scrape to persist the results.
The CSV lives at `/opt/data/apify_export.csv` (Railway persistent volume).
Rows are appended — existing data is never overwritten.

## Immoweb actor

- Actor ID: `UUjIYNdzU5Mo8szQN`
- Name: Immoweb Belgian Real Estate Scraper
- Pricing: $1.00 / 1 000 résultats

## Commands

```bash
# Append items from a JSON array
python3 /opt/data/skills/csv-export/append_csv.py '<json_array>'

# Run the Immoweb actor and export in one step
python3 /opt/data/skills/csv-export/run_and_export.py '{"startUrls": [...]}'
```
