# BrainBox QA Local API (v4) — No AWS, with Local "Athena" via SQLite

- CSV validation & upload (simulated S3 + Glue markers under `local_state/`)
- **Local SQL** via SQLite simulating Athena:
  - Database: `bills_db` → file: `local_state/db/bills_db.sqlite`
  - Table (simulated schema): `custom_csv`

## Endpoints (both with/without trailing slash)
- `POST /validate` — exact header + basic type checks (ints, ISO dates)
- `POST /upload` — validates, stores CSV under `local_state/uploads/`, writes a Glue marker, **loads rows into SQLite** (`custom_csv`)
- `POST /athena/query` — run **SELECT-only** SQL; returns `columns`, `rows`, `rowcount`

## Required CSV Header (exact)
bill_id, meter_id, usage_type, building_id, start_date, end_date

## Quickstart
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Validate:
curl -i -X POST -F "file=@sample_data/valid_bills.csv" http://localhost:8000/validate/

# Upload (saves + marker + loads into DB):
curl -i -X POST -F "file=@sample_data/valid_bills.csv" http://localhost:8000/upload/

# Query via local Athena (SQLite):
curl -s -X POST http://localhost:8000/athena/query/ \
  -H "Content-Type: application/json" \
  -d '{"sql":"SELECT COUNT(*) AS c FROM custom_csv"}' | jq

## Artifacts
- local_state/uploads/ — stored CSVs
- local_state/glue/ — crawler `.marker` files
- local_state/db/bills_db.sqlite — SQLite DB

Notes:
- Both `/path` and `/path/` registered (no 307 surprises).
- `/athena/query` accepts **SELECT** only (guarded) and returns up to 1000 rows.
