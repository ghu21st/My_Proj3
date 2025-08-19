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
