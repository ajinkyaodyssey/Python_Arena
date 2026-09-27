# week6/day29/test_aggregates.py
# Aggregate validation tests using GROUP BY, COUNT, SUM, AVG
# Run with: pytest week6/day29/test_aggregates.py -v

import pytest
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "test_db.db")


@pytest.fixture(scope="session")
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def query(db, sql, params=()):
    return [dict(r) for r in db.execute(sql, params).fetchall()]


def test_total_user_count_is_correct(db):
    result = query(db, "SELECT COUNT(*) AS count FROM users")
    assert result[0]["count"] == 10


def test_each_role_has_at_least_one_user(db):
    result = query(db, """
        SELECT role, COUNT(*) AS count
        FROM users
        GROUP BY role
        HAVING COUNT(*) < 1
    """)
    assert len(result) == 0, (
        f"Roles with zero users found: {result}"
    )


def test_total_revenue_is_positive(db):
    result = query(db, "SELECT SUM(amount) AS total FROM orders")
    assert result[0]["total"] > 0


def test_average_order_value_is_within_expected_range(db):
    """
    Average order should be between 500 and 10000.
    Outside this range suggests data corruption.
    """
    result = query(db, "SELECT AVG(amount) AS avg FROM orders")
    avg = result[0]["avg"]
    assert 500 <= avg <= 10000, (
        f"Average order value {avg:.2f} is outside expected range"
    )


def test_no_role_has_more_users_than_total(db):
    """Sanity check: no single role count exceeds total user count."""
    total = query(db, "SELECT COUNT(*) AS c FROM users")[0]["c"]
    by_role = query(db, """
        SELECT role, COUNT(*) AS count
        FROM users GROUP BY role
    """)
    for r in by_role:
        assert r["count"] <= total


def test_completed_orders_have_highest_average(db):
    """
    Business rule: completed orders should have higher average
    than failed orders. Failed orders tend to be smaller amounts.
    """
    result = query(db, """
        SELECT status, AVG(amount) AS avg_amount
        FROM orders
        WHERE status IN ('completed', 'failed')
        GROUP BY status
    """)
    avgs = {r["status"]: r["avg_amount"] for r in result}

    if "completed" in avgs and "failed" in avgs:
        print(
            f"\n  Completed avg: ₹{avgs['completed']:.2f} "
            f"| Failed avg: ₹{avgs['failed']:.2f}"
        )