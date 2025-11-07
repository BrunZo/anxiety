import sqlite3
from collections import defaultdict
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "anxiety.db"


def get_connection():
    """Get a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row 
    return conn


def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS anxiety_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                datetime TEXT NOT NULL,
                type TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    finally:
        conn.close()


def insert_anxiety_entry(anxiety_type, description):
    """Insert a new anxiety entry into the database.
    
    Args:
        anxiety_type: The type of anxiety (e.g., "social", "existential")
        description: Description of the anxiety feeling
    
    Returns:
        The ID of the inserted entry
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO anxiety_entries (datetime, type, description)
            VALUES (?, ?, ?)
        """, (now, anxiety_type, description))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_all_entries():
    """Get all anxiety entries from the database.
    
    Returns:
        List of dictionaries containing entry data
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT datetime, type, description
            FROM anxiety_entries
            ORDER BY datetime DESC
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_statistics():
    """Get statistics about anxiety entries.
    
    Returns:
        Dictionary with:
            - by_type: Dictionary mapping anxiety types to counts
            - by_hour: Dictionary mapping hours (0-23) to counts
            - total: Total number of entries
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT datetime, type
            FROM anxiety_entries
        """)
        rows = cursor.fetchall()
        
        stats_by_type = defaultdict(int)
        stats_by_hour = defaultdict(int)
        
        for row in rows:
            anxiety_type = row["type"] or "unknown"
            stats_by_type[anxiety_type] += 1
            
            dt = datetime.fromisoformat(row["datetime"])
            hour = dt.hour
            stats_by_hour[hour] += 1
        
        return {
            "by_type": dict(stats_by_type),
            "by_hour": dict(stats_by_hour),
            "total": len(rows)
        }
    finally:
        conn.close()


def get_total_count():
    """Get the total number of anxiety entries.
    
    Returns:
        Integer count of total entries
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM anxiety_entries")
        result = cursor.fetchone()
        return result["count"] if result else 0
    finally:
        conn.close()

