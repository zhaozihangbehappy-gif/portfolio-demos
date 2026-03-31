# CRM API Sync Demo

Portfolio demo that pulls paginated CRM-style records from a mock API payload, normalizes them, and syncs them into SQLite with upsert logic, logging, and error handling.

## What this demo shows

- Paginated API ingestion
- Incremental sync logic
- SQLite upserts
- Structured logging
- Basic retry-ready architecture and error handling
- Optional volume simulation to stress-test the sync workflow at 10K+ rows

## Files

- `sync_crm_demo.py` - sync script
- `data/mock_crm_page_1.json`
- `data/mock_crm_page_2.json`
- `output/crm_sync.db` - generated SQLite database
- `logs/crm_sync.log` - execution log

## Run

```bash
python sync_crm_demo.py
```

To stress-test the sync volume:

```bash
python sync_crm_demo.py --simulate-records 12000
```

## Database tables

- `contacts`

Each record is upserted by `contact_id`.

## Notes

This is a portfolio demo built to represent an internal CRM sync workflow. It uses mock paginated payloads so the integration pattern is fully reproducible.
