import sqlite3
import datetime
from config import TRACKING_DB_PATH

def get_tracking_connection():
    return sqlite3.connect(TRACKING_DB_PATH)

def init_tracking_db():
    with get_tracking_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checked_rows (
                reference_no TEXT PRIMARY KEY,
                checked_at TEXT,
                checked_by TEXT
            )
        ''')
        conn.commit()

def mark_as_checked(ref, username):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_tracking_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO checked_rows (reference_no, checked_at, checked_by)
            VALUES (?, ?, ?)
        ''', (str(ref), timestamp, username))
        conn.commit()

def unmark_as_checked(ref):
    with get_tracking_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM checked_rows WHERE reference_no = ?', (str(ref),))
        conn.commit()

def get_checked_refs():
    with get_tracking_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT reference_no FROM checked_rows")
        return {row[0] for row in cursor.fetchall()}
