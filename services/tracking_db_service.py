import sqlite3
import datetime
from config import TRACKING_DB_PATH

def get_tracking_connection():
    return sqlite3.connect(TRACKING_DB_PATH)

def init_tracking_db():
    with get_tracking_connection() as conn:
        cursor = conn.cursor()
        
        # Create table with composite primary key (reference_no, checked_by)
        # This allows multiple users to track the same reference number independently
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checked_rows (
                reference_no TEXT,
                checked_at TEXT,
                checked_by TEXT,
                PRIMARY KEY (reference_no, checked_by)
            )
        ''')
        
        # Migration: if old table exists without checked_by in PK, recreate it
        cursor.execute("PRAGMA table_info(checked_rows)")
        columns = cursor.fetchall()
        if columns:
            # Check if checked_by is part of primary key
            pk_columns = [c for c in columns if c[5] == 1]  # pk column
            pk_names = [c[1] for c in pk_columns]
            if "checked_by" not in pk_names:
                # Old schema - migrate data and recreate
                cursor.execute('''
                    CREATE TABLE checked_rows_new (
                        reference_no TEXT,
                        checked_at TEXT,
                        checked_by TEXT,
                        PRIMARY KEY (reference_no, checked_by)
                    )
                ''')
                cursor.execute('''
                    INSERT INTO checked_rows_new (reference_no, checked_at, checked_by)
                    SELECT reference_no, checked_at, checked_by FROM checked_rows
                ''')
                cursor.execute('DROP TABLE checked_rows')
                cursor.execute('ALTER TABLE checked_rows_new RENAME TO checked_rows')
        
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

def unmark_as_checked(ref, username):
    with get_tracking_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM checked_rows WHERE reference_no = ? AND checked_by = ?', (str(ref), username))
        conn.commit()

def get_checked_refs(username):
    """Get reference numbers checked by a specific user."""
    with get_tracking_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT reference_no FROM checked_rows WHERE checked_by = ?", (username,))
        return {row[0] for row in cursor.fetchall()}

def get_all_checked_refs():
    """Get all checked references with usernames (for admin/debug)."""
    with get_tracking_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT reference_no, checked_by, checked_at FROM checked_rows")
        return cursor.fetchall()