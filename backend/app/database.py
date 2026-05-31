import sqlite3
from app.config import settings

def get_db_connection():
    conn = sqlite3.connect(settings.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create conversation history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Conversation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create denomination preferences table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Preferences (
        session_id TEXT PRIMARY KEY,
        denomination TEXT NOT NULL
    )
    """)
    
    # Create evaluations results table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Evaluation (
        test_id TEXT PRIMARY KEY,
        category TEXT NOT NULL,
        test_case TEXT NOT NULL,
        result TEXT NOT NULL,
        score REAL NOT NULL,
        llm_response TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create global status table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS GlobalStatus (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """)
    
    conn.commit()
    conn.close()

# History Helpers
def save_message(session_id: str, role: str, message: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Conversation (session_id, role, message) VALUES (?, ?, ?)",
        (session_id, role, message)
    )
    conn.commit()
    conn.close()

def get_history(session_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, message, timestamp FROM Conversation WHERE session_id = ? ORDER BY id ASC",
        (session_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"role": r["role"], "message": r["message"], "timestamp": r["timestamp"]} for r in rows]

# Preference Helpers
def save_preference(session_id: str, denomination: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Preferences (session_id, denomination) VALUES (?, ?) ON CONFLICT(session_id) DO UPDATE SET denomination=excluded.denomination",
        (session_id, denomination)
    )
    conn.commit()
    conn.close()

def get_preference(session_id: str) -> str:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT denomination FROM Preferences WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row["denomination"]
    return "Protestant"  # Default fallback

# Evaluation Helpers
def save_evaluation(test_id: str, category: str, test_case: str, result: str, score: float, llm_response: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Evaluation (test_id, category, test_case, result, score, llm_response) VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT(test_id) DO UPDATE SET result=excluded.result, score=excluded.score, llm_response=excluded.llm_response, timestamp=CURRENT_TIMESTAMP",
        (test_id, category, test_case, result, score, llm_response)
    )
    conn.commit()
    conn.close()

def get_evaluations():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT test_id, category, test_case, result, score, llm_response, timestamp FROM Evaluation")
    rows = cursor.fetchall()
    conn.close()
    return [{
        "test_id": r["test_id"],
        "category": r["category"],
        "test_case": r["test_case"],
        "result": r["result"],
        "score": r["score"],
        "llm_response": r["llm_response"],
        "timestamp": r["timestamp"]
    } for r in rows]

def clear_evaluations():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Evaluation")
    conn.commit()
    conn.close()

# Global Status Helpers
def set_status(key: str, value: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO GlobalStatus (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value)
    )
    conn.commit()
    conn.close()

def get_status(key: str) -> str:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM GlobalStatus WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row["value"] if row else "False"
