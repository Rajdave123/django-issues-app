"""Small JSON-file repository used by the API."""

import json
import threading
from pathlib import Path

from django.conf import settings

_lock = threading.RLock()


def _path(filename):
    return Path(settings.BASE_DIR) / filename


def read_records(filename):
    path = _path(filename)
    with _lock:
        if not path.exists():
            return []
        try:
            with path.open("r", encoding="utf-8") as data_file:
                records = json.load(data_file)
        except (json.JSONDecodeError, OSError) as exc:
            raise RuntimeError(f"Could not read {filename}") from exc
        if not isinstance(records, list):
            raise RuntimeError(f"{filename} must contain a JSON array")
        return records


def write_records(filename, records):
    path = _path(filename)
    with _lock:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        try:
            with temporary.open("w", encoding="utf-8", newline="\n") as data_file:
                json.dump(records, data_file, ensure_ascii=False, indent=2)
                data_file.write("\n")
            temporary.replace(path)
        except OSError as exc:
            temporary.unlink(missing_ok=True)
            raise RuntimeError(f"Could not write {filename}") from exc


def next_id(records):
    ids = [record.get("id") for record in records if isinstance(record.get("id"), int)]
    return max(ids, default=0) + 1
