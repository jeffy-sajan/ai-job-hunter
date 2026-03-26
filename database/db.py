import sqlite3
from pathlib import Path
from typing import Dict, Tuple


DB_PATH = Path(__file__).resolve().parent.parent / "data" / "jobs.db"


def get_connection() -> sqlite3.Connection:
	DB_PATH.parent.mkdir(parents=True, exist_ok=True)
	return sqlite3.connect(DB_PATH)


def init_db() -> None:
	conn = get_connection()
	try:
		cur = conn.cursor()
		cur.execute(
			"""
			CREATE TABLE IF NOT EXISTS jobs (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				title TEXT,
				company TEXT,
				link TEXT UNIQUE,
				score INTEGER,
				created_at TEXT DEFAULT (datetime('now'))
			);
			"""
		)
		conn.commit()
	finally:
		conn.close()


def insert_job(job: Dict[str, str], score: int) -> Tuple[bool, str | None]:
	"""Insert a job if link is new.

	Returns (inserted, error_message).
	"""

	conn = get_connection()
	try:
		cur = conn.cursor()
		cur.execute(
			"""
			INSERT INTO jobs (title, company, link, score)
			VALUES (?, ?, ?, ?)
			""",
			(job.get("title"), job.get("company"), job.get("link"), int(score)),
		)
		conn.commit()
		return True, None
	except sqlite3.IntegrityError as exc:
		# Most likely UNIQUE(link) violation
		return False, str(exc)
	except Exception as exc:  # pragma: no cover - generic safety
		return False, str(exc)
	finally:
		conn.close()


