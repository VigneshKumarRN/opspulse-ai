"""OpsPulse storage layer — saves parsed log records to SQLite."""
import sqlite3
from log_parser import read_logs

DB_PATH = "opspulse.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def create_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS job_logs (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            job       TEXT NOT NULL,
            status    TEXT NOT NULL,
            code      TEXT,
            message   TEXT
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_job ON job_logs(job)")
    conn.commit()


def insert_records(conn, records):
    rows = [(r.timestamp, r.job, r.status, r.code, r.message) for r in records]
    conn.executemany(
        "INSERT INTO job_logs (timestamp, job, status, code, message) VALUES (?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    return len(rows)


def failures_per_job(conn):
    return conn.execute("""
        SELECT job, COUNT(*) AS failures
        FROM job_logs
        WHERE status = 'FAILED'
        GROUP BY job
        ORDER BY failures DESC
    """).fetchall()


if __name__ == "__main__":
    conn = get_connection()
    create_table(conn)
    conn.execute("DELETE FROM job_logs")  # reset so reruns don't duplicate
    count = insert_records(conn, read_logs("sample_logs.txt"))
    print(f"Inserted {count} records.\n")
    print("Failures per job:")
    for job, n in failures_per_job(conn):
        print(f"  {job}: {n}")
    conn.close()