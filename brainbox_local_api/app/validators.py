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
