# backend/app/utils/file_utils.py
import tempfile
from pathlib import Path
from typing import Tuple


def write_temp_file(content: bytes, suffix: str = "") -> Tuple[str, Path]:
    """
    Write bytes to a temporary file and return (name, Path)
    Caller should delete file when done.
    """
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(content)
    tmp.flush()
    tmp.close()
    return tmp.name, Path(tmp.name)
