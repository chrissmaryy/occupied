import sqlite3
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path(__file__).resolve().parent.parent / "bathroom.db"

@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def fetch_one(query: str, params: tuple = ()):
    with get_connection() as conn:
        cur = conn.execute(query, params)
        return cur.fetchone()

def fetch_all(query: str, params: tuple = ()):
    with get_connection() as conn:
        cur = conn.execute(query, params)
        return cur.fetchall()

def execute(query: str, params: tuple = ()):
    with get_connection() as conn:
        conn.execute(query, params)

def execute_returning_id(query: str, params: tuple = ()):
    with get_connection() as conn:
        cur = conn.execute(query, params)
        return cur.lastrowid


def get_reservation_types():
    return fetch_all(
        "SELECT id, name, duration_minutes FROM reservation_types"
    )

def get_reservation_type_by_name(name: str):
    return fetch_one(
        "SELECT * FROM reservation_types WHERE name = ?",
        (name,)
    )

def create_reservation_entry(
    user_id: int,
    reservation_type_id: int,
    start_time: datetime,
    end_time: datetime
):
    return execute_returning_id(
        """
        INSERT INTO reservations (user_id, reservation_type_id, start_time, end_time)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, reservation_type_id, start_time, end_time)
    )

def get_reservations_between(start: str, end: str):
    return fetch_all(
        """
        SELECT * FROM reservations
        WHERE start_time < ?
          AND end_time   > ?
        """,
        (end, start)
    )

def get_reservation_types_between(start: str, end: str):
    return fetch_all(
        """
        SELECT reservation_type_id FROM reservations
        WHERE start_time < ?
          AND end_time   > ?
        """,
        (end, start)
    )

def get_reservations_user(user_id: int):
    return fetch_all(
        "SELECT * FROM reservations WHERE user_id = ?",
        (user_id)
    )

def get_reservation_by_id(reservation_id: int):
    return fetch_one(
        "SELECT * FROM reservations WHERE id = ?",
        (reservation_id,)
    )

def get_reservations_for_day(date: str):
    return fetch_all(
        """
        SELECT *
        FROM reservations
        WHERE start_time < datetime(?, '+1 day')
          AND end_time   > datetime(?)
        ORDER BY start_time
        """,
        (date, date)
    )

def update_reservation_entry(
    reservation_id: int,
    reservation_type_id: int,
    start_time: datetime,
    end_time: datetime
):
    execute(
        """
        UPDATE reservations
        SET reservation_type_id = ?, start_time = ?, end_time = ?
        WHERE id = ?
        """,
        (reservation_type_id, start_time, end_time, reservation_id)
    )


def delete_reservation_entry(reservation_id: int):
    execute(
        "DELETE FROM reservations WHERE id = ?",
        (reservation_id,)
    )

def create_user(username: str, password_hash: str):
    return execute_returning_id(
        """
        INSERT INTO users (username, password_hash, created_at)
        VALUES (?, ?, datetime('now'))
        """,
        (username, password_hash)
    )

def get_user_by_username(username: str):
    return fetch_one(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )

def get_user_by_id(user_id: int):
    return fetch_one(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    )
