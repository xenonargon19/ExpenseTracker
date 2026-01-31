import sqlite3
from pathlib import Path

# DB file stored inside your project folder
DB_PATH = Path(__file__).resolve().parent / "data.db"


def get_conn():
    """Open a DB connection. Caller must close()."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # access columns by name
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS targets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        weight INTEGER NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        type TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target_name TEXT NOT NULL,
        amount REAL NOT NULL,
        purchased_at TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS achievements (
        key TEXT PRIMARY KEY,
        achieved_at TEXT NOT NULL
    );
    """)



    conn.commit()
    conn.close()

def list_targets():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, price, weight FROM targets")
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def insert_target(name, price, weight):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO targets (name, price, weight) VALUES (?, ?, ?)",
        (name, price, weight),
    )
    conn.commit()
    new_id = cur.lastrowid
    return new_id



def update_target_weight(target_id, new_weight):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE targets SET weight = ? WHERE id = ?",
        (new_weight, target_id),
    )
    conn.commit()
    conn.close()


def delete_target(target_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM targets WHERE id = ?", (target_id,))
    conn.commit()
    conn.close()

def list_transactions():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, date, amount, category, type FROM transactions ORDER BY date DESC"
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def insert_transaction(date, amount, category, txn_type):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO transactions (date, amount, category, type) VALUES (?, ?, ?, ?)",
        (date, amount, category, txn_type),
    )
    conn.commit()
    conn.close()

def insert_purchase(target_name, amount, purchased_at):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO purchases (target_name, amount, purchased_at) VALUES (?, ?, ?)",
        (target_name, amount, purchased_at),
    )
    conn.commit()
    conn.close()


def list_purchases():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, target_name, amount, purchased_at FROM purchases ORDER BY purchased_at DESC"
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def clear_targets():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM targets")
    conn.commit()
    conn.close()

def achievement_exists(key):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT 1 FROM achievements WHERE key = ?",
        (key,)
    )
    row = cur.fetchone()

    conn.close()
    return row is not None

def insert_achievement(key, achieved_at):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO achievements (key, achieved_at) VALUES (?, ?)",
        (key, achieved_at)
    )

    conn.commit()
    conn.close()


def get_achieved_keys():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT key FROM achievements")
    rows = cur.fetchall()

    conn.close()
    return {row[0] for row in rows}

def clear_achievements():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("DELETE FROM achievements")

    conn.commit()
    conn.close()



