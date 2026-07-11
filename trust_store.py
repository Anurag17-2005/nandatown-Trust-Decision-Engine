"""
SQLite trust history database
Stores agent reputation data and reports
"""
import sqlite3
from typing import List, Tuple, Optional
from datetime import datetime
import time
import uuid


DB_PATH = "trust_history.db"


def init_db():
    """Initialize database schema"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Trust history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trust_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT NOT NULL,
            outcome TEXT CHECK(outcome IN ('good', 'bad')) NOT NULL,
            receipt_hash TEXT NOT NULL,
            reporter_id TEXT,
            timestamp INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_agent ON trust_history(agent_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_timestamp ON trust_history(timestamp)
    """)
    
    # Service metadata table (stores TDE keypair)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS service_metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()


def add_report(agent_id: str, outcome: str, receipt_hash: str, reporter_id: str) -> str:
    """Add a new trust report"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    report_id = f"rep_{uuid.uuid4().hex[:12]}"
    timestamp = int(time.time())
    
    cursor.execute("""
        INSERT INTO trust_history (agent_id, outcome, receipt_hash, reporter_id, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (agent_id, outcome, receipt_hash, reporter_id, timestamp))
    
    conn.commit()
    conn.close()
    
    return report_id


def get_reports(agent_id: str) -> List[dict]:
    """Get all reports for an agent"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT outcome, receipt_hash, reporter_id, timestamp, created_at
        FROM trust_history
        WHERE agent_id = ?
        ORDER BY timestamp DESC
    """, (agent_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    reports = []
    for row in rows:
        reports.append({
            'outcome': row[0],
            'receipt_hash': row[1],
            'reporter_id': row[2],
            'timestamp': row[3],
            'created_at': row[4]
        })
    
    return reports


def compute_trust_score(agent_id: str) -> Tuple[float, float, int, int, int]:
    """
    Compute trust score using PR #129 formula: +1 good, -2 bad
    Returns: (trust_score, confidence, total_reports, good_count, bad_count)
    """
    reports = get_reports(agent_id)
    
    if not reports:
        return 0.5, 0.0, 0, 0, 0  # Unknown = neutral
    
    good = sum(1 for r in reports if r['outcome'] == 'good')
    bad = sum(1 for r in reports if r['outcome'] == 'bad')
    total = good + bad
    
    if total == 0:
        return 0.5, 0.0, 0, 0, 0
    
    # Raw score: -1.0 to +1.0
    raw_score = (good - 2 * bad) / total
    
    # Normalize to 0.0 to 1.0
    normalized = (raw_score + 1.0) / 2.0
    normalized = max(0.0, min(1.0, normalized))  # Clamp
    
    # Confidence: more data = higher confidence
    confidence = min(1.0, total / 50.0)
    
    return normalized, confidence, total, good, bad


def get_metadata(key: str) -> Optional[str]:
    """Get service metadata value"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT value FROM service_metadata WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    
    return row[0] if row else None


def set_metadata(key: str, value: str):
    """Set service metadata value"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO service_metadata (key, value)
        VALUES (?, ?)
    """, (key, value))
    
    conn.commit()
    conn.close()
