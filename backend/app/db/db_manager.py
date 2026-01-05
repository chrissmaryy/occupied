import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from contextlib import contextmanager
import secrets


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

#-------------------DB Helpers------------------------------------------------------
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

#-------------------Operations------------------------------------------------------

# Reservations
def create_reservation_entry(
    user_id: int,
    is_private: bool,
    start_time: datetime,
    end_time: datetime
) -> int:
    return execute_returning_id(
        """
        INSERT INTO reservations (user_id, is_private, start_time, end_time)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, is_private, start_time, end_time)
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
    is_private: bool,
    start_time: datetime,
    end_time: datetime
):
    execute_returning_id(
        """
        UPDATE reservations
        SET is_private = ?, start_time = ?, end_time = ?
        WHERE id = ?
        """,
        (is_private, start_time, end_time, reservation_id)
    )

def delete_reservation_entry(reservation_id: int):
    execute(
        "DELETE FROM reservations WHERE id = ?",
        (reservation_id,)
    )

# User
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

# Sessions
SESSION_TTL = timedelta(days=7)

def create_session(user_id: int) -> str:
    session_id = secrets.token_urlsafe(32)
    expires_at = datetime.now() + SESSION_TTL

    execute(
        """
        INSERT INTO sessions (id, user_id, expires_at)
        VALUES (?, ?, ?)
        """,
        (session_id, user_id, expires_at)
    )

    return session_id

def get_session(session_id: str):
    return fetch_one(
        """
        SELECT *
        FROM sessions
        WHERE id = ?
          AND expires_at > ?
        """,
        (session_id, datetime.utcnow())
    )

def delete_session(session_id: str):
    execute(
        "DELETE FROM sessions WHERE id = ?",
        (session_id,)
    )

##-------------------Specific Helpers------------------------------------------------
def is_reservation_active(reservation_id: int) -> bool:
    reservation = get_reservation_by_id(reservation_id)
    return datetime.now() >= reservation["start_time"] and datetime.now() <= reservation["end_time"]

def time_until_end(reservation_id: int) -> timedelta:
    reservation = get_reservation_by_id(reservation_id)
    return reservation["end_time"] - datetime.now()