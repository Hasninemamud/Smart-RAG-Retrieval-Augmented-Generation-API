# backend/app/services/db_extraction.py
import sqlite3
import io
import tempfile
from pathlib import Path
from typing import List


def read_sqlite_db(file_bytes: bytes) -> str:
    """
    Write bytes to a temporary file and return a flattened text representation
    of table names, columns and up to 1000 rows per table.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp.flush()
        tmp_path = tmp.name

    conn = sqlite3.connect(tmp_path)
    cursor = conn.cursor()
    out_lines = []
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cursor.fetchall()]
    for t in tables:
        cursor.execute(f'SELECT * FROM "{t}" LIMIT 1000')
        rows = cursor.fetchall()
        cols = [c[0] for c in cursor.description] if cursor.description else []
        out_lines.append(f"Table: {t}\nColumns: {cols}\nRows:")
        for r in rows:
            out_lines.append(str(r))
    conn.close()
    # delete temp file
    try:
        Path(tmp_path).unlink(missing_ok=True)
    except Exception:
        pass
    return "\n".join(out_lines)
