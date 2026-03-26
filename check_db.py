#!/usr/bin/env python3
"""Small helper to inspect the SQLite jobs DB.

Usage:
  python check_db.py
  python check_db.py --db data/jobs.db
"""
import argparse
import sqlite3
import sys


def main(db_path: str) -> int:
    try:
        conn = sqlite3.connect(db_path)
    except Exception as e:
        print(f"Failed to open DB '{db_path}':", e)
        return 2

    cur = conn.cursor()
    try:
        cur.execute("SELECT count(*) FROM jobs")
        count = cur.fetchone()[0]
    except Exception as e:
        print("Error querying DB:", e)
        conn.close()
        return 3

    print("count:", count)
    print("\nLast 5 jobs:")
    try:
        for row in cur.execute(
            "SELECT id, title, company, link, score FROM jobs ORDER BY id DESC LIMIT 5"
        ):
            print(row)
    except Exception as e:
        print("Error fetching rows:", e)

    conn.close()
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--db", "-d", default="data/jobs.db", help="Path to SQLite DB")
    args = p.parse_args()
    sys.exit(main(args.db))
