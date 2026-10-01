# week6/day31/db_helpers.py
# Reusable DB helpers for test validation.
# Import this in any test file that needs DB access.

import sqlite3
import os
from contextlib import contextmanager
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "test_db.db")


@contextmanager
def get_db():
    """
    Context manager for DB connection.
    Always closes connection even if test fails.
    Uses row_factory so rows behave like dicts.

    Usage:
        with get_db() as db:
            rows = db.execute("SELECT * FROM users").fetchall()
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def fetch_all(sql: str, params: tuple = ()) -> list[dict]:
    """Run SELECT, return list of dicts."""
    with get_db() as conn:
        cursor = conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]


def fetch_one(sql: str, params: tuple = ()) -> Optional[dict]:
    """Run SELECT, return first row as dict or None."""
    with get_db() as conn:
        cursor = conn.execute(sql, params)
        row = cursor.fetchone()
        return dict(row) if row else None


def fetch_value(sql: str, params: tuple = ()):
    """Run SELECT, return single scalar value."""
    with get_db() as conn:
        cursor = conn.execute(sql, params)
        row = cursor.fetchone()
        return row[0] if row else None


def execute(sql: str, params: tuple = ()) -> int:
    """
    Run INSERT/UPDATE/DELETE.
    Returns rowcount (how many rows affected).
    Commits automatically.
    """
    with get_db() as conn:
        cursor = conn.execute(sql, params)
        conn.commit()
        return cursor.rowcount


def user_exists(user_id: int) -> bool:
    """Check if a user with given id exists."""
    result = fetch_value(
        "SELECT COUNT(*) FROM users WHERE id = ?",
        (user_id,)
    )
    return result > 0


def order_exists(order_id: int) -> bool:
    """Check if an order with given id exists."""
    result = fetch_value(
        "SELECT COUNT(*) FROM orders WHERE id = ?",
        (order_id,)
    )
    return result > 0


def get_user(user_id: int) -> Optional[dict]:
    """Fetch a single user by id."""
    return fetch_one(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    )


def get_orders_for_user(user_id: int) -> list[dict]:
    """Fetch all orders for a given user."""
    return fetch_all(
        "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at",
        (user_id,)
    )


def count_rows(table: str, where: str = "", params: tuple = ()) -> int:
    """
    Count rows in a table with optional WHERE clause.

    Usage:
        count_rows("users")
        count_rows("users", "WHERE status = ?", ("active",))
        count_rows("orders", "WHERE amount > ?", (1000,))
    """
    sql = f"SELECT COUNT(*) FROM {table} {where}"
    return fetch_value(sql, params)