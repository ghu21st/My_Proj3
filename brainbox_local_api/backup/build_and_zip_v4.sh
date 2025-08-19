#!/usr/bin/env bash
set -euo pipefail

ROOT="$(pwd)/brainbox_qa_local_api_v4"
mkdir -p "$ROOT" && cd "$ROOT"
mkdir -p app tests/unit tests/integration docs sample_data local_state/uploads local_state/glue local_state/db

cat > README.md <<'EOF'
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
pytest -q
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
EOF

cat > requirements.txt <<'EOF'
fastapi==0.111.0
uvicorn==0.30.3
pydantic==2.8.2
python-multipart==0.0.9
pytest==8.2.0
httpx==0.27.0
EOF

cat > docs/integration_strategy.md <<'EOF'
# Integration Strategy (AWS)
If you wire real AWS later:
- S3: put_object CSV
- Glue: start_crawler + poll READY
- Athena: run SELECT COUNT(*) FROM custom_csv and poll SUCCEEDED
EOF

cat > app/__init__.py <<'EOF'
# package
EOF

cat > app/schemas.py <<'EOF'
REQUIRED_COLUMNS = [
    "bill_id",
    "meter_id",
    "usage_type",
    "building_id",
    "start_date",
    "end_date",
]
EOF

cat > app/validators.py <<'EOF'
import csv, io
from datetime import datetime
from typing import Tuple, List, Dict
from .schemas import REQUIRED_COLUMNS

def parse_csv(content: bytes) -> Tuple[List[str], List[Dict[str,str]]]:
    text = content.decode("utf-8", errors="strict")
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None:
        raise ValueError("InvalidCSV: No header found")
    header = [h.strip() for h in reader.fieldnames]
    rows = []
    for r in reader:
        rows.append({(k.strip() if k is not None else k): (v.strip() if v is not None else v) for k,v in r.items()})
    return header, rows

def validate_header_exact(header: List[str]) -> Tuple[bool, dict]:
    missing = [c for c in REQUIRED_COLUMNS if c not in header]
    extra = [c for c in header if c not in REQUIRED_COLUMNS]
    ok = (len(missing) == 0 and len(extra) == 0)
    return ok, {"missing": missing, "extra": extra}

def is_iso_date(s: str) -> bool:
    try:
        datetime.fromisoformat(s)
        return True
    except Exception:
        return False

def validate_basic_types(rows: List[Dict[str,str]], sample_n: int = 100) -> Tuple[bool, dict]:
    sample = rows[:sample_n]
    for i, r in enumerate(sample, start=1):
        if not r.get("bill_id"): return False, {"row": i, "field":"bill_id", "expected":"string(non-empty)"}
        if not r.get("usage_type"): return False, {"row": i, "field":"usage_type", "expected":"string(non-empty)"}
        try: int(r.get("meter_id",""))
        except Exception: return False, {"row": i, "field":"meter_id", "expected":"integer"}
        try: int(r.get("building_id",""))
        except Exception: return False, {"row": i, "field":"building_id", "expected":"integer"}
        if not is_iso_date(r.get("start_date","")): return False, {"row": i, "field":"start_date", "expected":"ISO date"}
        if not is_iso_date(r.get("end_date","")): return False, {"row": i, "field":"end_date", "expected":"ISO date"}
    return True, {}
EOF

cat > app/services.py <<'EOF'
from pathlib import Path
import uuid, time

class LocalMockAws:
    """Simulates S3 (uploads/) and Glue (glue/ markers)."""
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.state_root = self.project_root / "local_state"
        self.uploads = self.state_root / "uploads"
        self.glue = self.state_root / "glue"
        self.uploads.mkdir(parents=True, exist_ok=True)
        self.glue.mkdir(parents=True, exist_ok=True)

    def put_csv(self, content: bytes, filename: str | None = None) -> Path:
        name = filename or f"upload__{uuid.uuid4().hex}.csv"
        path = self.uploads / name
        path.write_bytes(content)
        return path

    def trigger_glue_crawler(self, crawler_name: str = "bills_crawler") -> Path:
        marker = self.glue / f"{crawler_name}__{int(time.time())}__{uuid.uuid4().hex}.marker"
        marker.write_text("ok")
        return marker
EOF

cat > app/db.py <<'EOF'
import sqlite3
from pathlib import Path
from typing import List, Dict, Tuple

DB_DIRNAME = "local_state/db"
DB_FILENAME = "bills_db.sqlite"
TABLE_NAME = "custom_csv"

def get_db_path(project_root: Path) -> Path:
    db_dir = project_root / DB_DIRNAME
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / DB_FILENAME

def init_db(project_root: Path) -> None:
    db_path = get_db_path(project_root)
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                bill_id TEXT NOT NULL,
                meter_id INTEGER NOT NULL,
                usage_type TEXT NOT NULL,
                building_id INTEGER NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL
            )
        """)
        conn.commit()

def load_rows(project_root: Path, rows: List[Dict[str, str]]) -> int:
    db_path = get_db_path(project_root)
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        to_insert = []
        for r in rows:
            to_insert.append((
                r.get("bill_id",""),
                int(r.get("meter_id","0") or 0),
                r.get("usage_type",""),
                int(r.get("building_id","0") or 0),
                r.get("start_date",""),
                r.get("end_date",""),
            ))
        cur.executemany(f"""
            INSERT INTO {TABLE_NAME} (bill_id, meter_id, usage_type, building_id, start_date, end_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, to_insert)
        conn.commit()
        return len(to_insert)

def run_select(project_root: Path, sql: str, max_rows: int = 1000) -> Tuple[List[str], List[Tuple]]:
    db_path = get_db_path(project_root)
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(sql)
        cols = [d[0] for d in cur.description] if cur.description else []
        rows = cur.fetchall()
        return cols, rows[:max_rows]
EOF

cat > app/main.py <<'EOF'
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pathlib import Path

from .validators import parse_csv, validate_header_exact, validate_basic_types
from .services import LocalMockAws
from . import db as localdb

app = FastAPI(title="BrainBox QA Local API v4", version="1.0.0")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
aws = LocalMockAws(PROJECT_ROOT)
localdb.init_db(PROJECT_ROOT)  # ensure DB/table on startup

class QueryIn(BaseModel):
    sql: str

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/validate")
@app.post("/validate/")
async def validate(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        return JSONResponse(status_code=415, content={"error":"InvalidFileType","message":"Only .csv accepted."})
    try:
        content = await file.read()
        header, rows = parse_csv(content)
    except UnicodeDecodeError:
        return JSONResponse(status_code=400, content={"error":"InvalidEncoding","message":"CSV must be UTF-8."})
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error":"InvalidCSV","message":str(e)})

    ok_schema, info = validate_header_exact(header)
    if not ok_schema:
        return JSONResponse(status_code=422, content={"error":"InvalidSchema", **info})

    ok_types, tinfo = validate_basic_types(rows)
    if not ok_types:
        return JSONResponse(status_code=422, content={"error":"InvalidType", **tinfo})

    return {"message":"CSV file is valid.","columns": header, "rows_checked": min(100, len(rows))}

@app.post("/upload")
@app.post("/upload/")
async def upload(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        return JSONResponse(status_code=415, content={"error":"InvalidFileType","message":"Only .csv accepted."})
    try:
        content = await file.read()
        header, rows = parse_csv(content)
    except UnicodeDecodeError:
        return JSONResponse(status_code=400, content={"error":"InvalidEncoding","message":"CSV must be UTF-8."})
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error":"InvalidCSV","message":str(e)})

    ok_schema, info = validate_header_exact(header)
    if not ok_schema:
        return JSONResponse(status_code=422, content={"error":"InvalidSchema", **info})

    ok_types, tinfo = validate_basic_types(rows)
    if not ok_types:
        return JSONResponse(status_code=422, content={"error":"InvalidType", **tinfo})

    # Save CSV & simulate Glue
    saved_path = aws.put_csv(content, filename=file.filename)
    marker_path = aws.trigger_glue_crawler("bills_crawler")

    # Load into SQLite (bills_db.custom_csv)
    localdb.init_db(PROJECT_ROOT)
    inserted = localdb.load_rows(PROJECT_ROOT, rows)

    return {
        "status":"ok",
        "stored": str(saved_path.relative_to(PROJECT_ROOT)),
        "crawler_marker": str(marker_path.relative_to(PROJECT_ROOT)),
        "rows_inserted": inserted
    }

@app.post("/athena/query")
@app.post("/athena/query/")
async def athena_query(q: QueryIn):
    sql = q.sql.strip().rstrip(";")
    if not sql.lower().startswith("select"):
        return JSONResponse(status_code=400, content={"error":"OnlySelectAllowed","message":"Only SELECT statements are allowed."})
    try:
        cols, rows = localdb.run_select(PROJECT_ROOT, sql, max_rows=1000)
        return {"columns": cols, "rows": rows, "rowcount": len(rows)}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error":"QueryError","message": str(e)})
EOF

cat > tests/unit/test_header.py <<'EOF'
from app.validators import validate_header_exact

def test_validate_header_exact_all_good():
    ok, info = validate_header_exact(["bill_id","meter_id","usage_type","building_id","start_date","end_date"])
    assert ok and info["missing"] == [] and info["extra"] == []

def test_validate_header_exact_extra():
    ok, info = validate_header_exact(["bill_id","meter_id","usage_type","building_id","start_date","end_date","foo"])
    assert ok is False
    assert "foo" in info["extra"]
EOF

cat > tests/unit/test_types.py <<'EOF'
from app.validators import validate_basic_types

def test_validate_basic_types_good():
    rows=[{"bill_id":"b1","meter_id":"1","usage_type":"kwh","building_id":"10","start_date":"2024-01-01","end_date":"2024-02-01"}]
    ok, info = validate_basic_types(rows)
    assert ok is True

def test_validate_basic_types_bad_meter():
    rows=[{"bill_id":"b1","meter_id":"x","usage_type":"kwh","building_id":"10","start_date":"2024-01-01","end_date":"2024-02-01"}]
    ok, info = validate_basic_types(rows)
    assert ok is False and info["field"]=="meter_id"
EOF

cat > tests/integration/test_api.py <<'EOF'
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_validate_missing_and_extra():
    files = {"file": ("bad.csv", b"bill_id,meter_id,usage_type,badcol\n1,2,3,4\n", "text/csv")}
    r = client.post("/validate/", files=files)
    assert r.status_code == 422
    body = r.json()
    assert body["error"] == "InvalidSchema"
    assert "building_id" in body["missing"]
    assert "badcol" in body["extra"]

def test_validate_ok_both_paths():
    header = b"bill_id,meter_id,usage_type,building_id,start_date,end_date\n"
    row = b"b1,1,kwh,10,2024-01-01,2024-02-01\n"
    for path in ("/validate", "/validate/"):
        r = client.post(path, files={"file":("ok.csv", header+row, "text/csv")})
        assert r.status_code == 200
        assert r.json()["message"].startswith("CSV file is valid")

def test_upload_query_roundtrip():
    header = b"bill_id,meter_id,usage_type,building_id,start_date,end_date\n"
    row = b"b1,1,kwh,10,2024-01-01,2024-02-01\n"
    r = client.post("/upload/", files={"file":("ok.csv", header+row, "text/csv")})
    assert r.status_code == 200, r.text
    assert r.json()["rows_inserted"] >= 1

    r2 = client.post("/athena/query/", json={"sql":"SELECT COUNT(*) AS c FROM custom_csv"})
    assert r2.status_code == 200, r2.text
    out = r2.json()
    assert out["columns"] == ["c"]
    assert out["rowcount"] == 1
    assert out["rows"][0][0] >= 1
EOF

cat > sample_data/valid_bills.csv <<'EOF'
bill_id,meter_id,usage_type,building_id,start_date,end_date
b1,100,kwh,1,2024-01-01,2024-01-31
EOF

cat > sample_data/invalid_missing_field.csv <<'EOF'
bill_id,meter_id,usage_type
b1,10,kwh
EOF

cd "$ROOT/.."
zip -r brainbox_qa_local_api_v4.zip brainbox_qa_local_api_v4 >/dev/null
echo "✅ Created: $(pwd)/brainbox_qa_local_api_v4.zip"
