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
