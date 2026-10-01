# week6/day31/conftest.py
import pytest
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "test_db.db")


@pytest.fixture(scope="session")
def db_path():
    """Path to the test database."""
    assert os.path.exists(DB_PATH), (
        f"Test DB not found at {DB_PATH}. "
        f"Run: cp week6/day30/test_db.db week6/day31/"
    )
    return DB_PATH


@pytest.fixture(scope="function")
def db(db_path):
    """
    Function-scoped DB connection.
    Fresh connection per test — no state leakage.
    Rolls back any changes made during the test
    so each test starts with clean data.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.rollback()
    conn.close()


@pytest.fixture(scope="function")
def db_write(db_path):
    """
    DB connection for tests that need to write data.
    Commits changes AND cleans up after itself.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    inserted_ids = {"users": [], "orders": []}
    yield conn, inserted_ids

    # Cleanup — remove anything this test inserted
    for order_id in inserted_ids["orders"]:
        conn.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    for user_id in inserted_ids["users"]:
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()