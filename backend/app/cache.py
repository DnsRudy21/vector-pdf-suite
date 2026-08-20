import hashlib
import json
import sqlite3
import time
from pathlib import Path
from threading import Lock


class DiskCache:
    def __init__(self, root: Path, ttl: int, max_bytes: int) -> None:
        self.root = root / "cache"
        self.root.mkdir(parents=True, exist_ok=True)
        self.ttl, self.max_bytes = ttl, max_bytes
        self.db_path = self.root / "cache.sqlite3"
        self._lock = Lock()
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS entries (key TEXT PRIMARY KEY, path TEXT, size INTEGER, created REAL, accessed REAL)")

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path, timeout=10)

    @staticmethod
    def key(content: bytes, params: dict) -> str:
        digest = hashlib.sha256(content)
        digest.update(json.dumps(params, sort_keys=True).encode())
        return digest.hexdigest()

    def get(self, key: str) -> Path | None:
        with self._lock, self._connect() as db:
            row = db.execute("SELECT path, created FROM entries WHERE key=?", (key,)).fetchone()
            if not row:
                return None
            path = Path(row[0])
            if time.time() - row[1] > self.ttl or not path.exists():
                db.execute("DELETE FROM entries WHERE key=?", (key,))
                path.unlink(missing_ok=True)
                return None
            db.execute("UPDATE entries SET accessed=? WHERE key=?", (time.time(), key))
            return path

    def put(self, key: str, source: Path, suffix: str) -> Path:
        target = self.root / f"{key}{suffix}"
        source.replace(target)
        with self._lock, self._connect() as db:
            db.execute("INSERT OR REPLACE INTO entries VALUES (?, ?, ?, ?, ?)", (key, str(target), target.stat().st_size, time.time(), time.time()))
        self.cleanup()
        return target

    def cleanup(self) -> None:
        now = time.time()
        with self._lock, self._connect() as db:
            rows = db.execute("SELECT key,path,size,created FROM entries ORDER BY accessed ASC").fetchall()
            total = sum(row[2] for row in rows)
            for key, raw_path, size, created in rows:
                if now - created > self.ttl or total > self.max_bytes:
                    Path(raw_path).unlink(missing_ok=True)
                    db.execute("DELETE FROM entries WHERE key=?", (key,))
                    total -= size

