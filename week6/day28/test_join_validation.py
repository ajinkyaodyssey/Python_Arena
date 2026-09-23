# week6/day28/test_join_validation.py
# DB validation tests using JOINs
# Run with: pytest week6/day28/test_join_validation.py -v

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


def test_every_order_belongs_to_existing_user(db):
    """
    INNER JOIN test: no orphaned orders.
    Every order must have a valid user_id that exists in users table.
    Orphaned orders = data integrity bug.
    """
    orphaned = query(db, """
        SELECT o.id, o.user_id, o.product
        FROM orders o
        LEFT JOIN users u ON o.user_id = u.id
        WHERE u.id IS NULL
    """)
    assert len(orphaned) == 0, (
        f"Found orders with no matching user: {orphaned}"
    )


def test_completed_orders_have_users_with_emails(db):
    """
    INNER JOIN test: completed orders must have contactable users.
    If a user has a completed order but no email,
    we cannot send them a confirmation — business rule violation.
    """
    no_email_completed = query(db, """
        SELECT u.name, o.product
        FROM orders o
        INNER JOIN users u ON o.user_id = u.id
        WHERE o.status = 'completed'
        AND u.email IS NULL
    """)
    assert len(no_email_completed) == 0, (
        f"Completed orders with unreachable users: {no_email_completed}"
    )


def test_total_revenue_from_completed_orders(db):
    """
    INNER JOIN + aggregate: verify total revenue calculation.
    Use case: after payment tests, verify the total matches expected.
    """
    result = query(db, """
        SELECT SUM(o.amount) AS total_revenue
        FROM orders o
        INNER JOIN users u ON o.user_id = u.id
        WHERE o.status = 'completed'
    """)
    total = result[0]["total_revenue"]
    assert total > 0, "Total revenue must be positive"
    assert isinstance(total, float), "Revenue must be a number"
    print(f"\n  Total completed revenue: ₹{total:.2f}")


def test_users_with_no_orders_exist(db):
    """
    LEFT JOIN test: verify we can identify users who never ordered.
    This is the classic interview query.
    Use case: finding users for re-engagement campaigns.
    """
    no_orders = query(db, """
        SELECT u.id, u.name
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        WHERE o.id IS NULL
    """)
    assert len(no_orders) > 0, (
        "Expected some users with no orders in test data"
    )
    print(f"\n  Users with no orders: {[u['name'] for u in no_orders]}")


def test_no_user_has_more_than_five_orders(db):
    """
    LEFT JOIN + GROUP BY: verify no user exceeded order limit.
    Use case: after stress test, confirm no duplicate orders were created.
    """
    over_limit = query(db, """
        SELECT u.name, COUNT(o.id) AS order_count
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        GROUP BY u.id, u.name
        HAVING COUNT(o.id) > 5
    """)
    assert len(over_limit) == 0, (
        f"Users with too many orders: {over_limit}"
    )


def test_failed_orders_belong_to_active_users_only(db):
    """
    INNER JOIN test: failed orders should only exist for active users.
    A deleted user having a failed order suggests
    the deletion flow did not clean up properly.
    """
    deleted_with_failed = query(db, """
        SELECT u.name, u.status, o.product
        FROM orders o
        INNER JOIN users u ON o.user_id = u.id
        WHERE o.status = 'failed'
        AND u.status = 'deleted'
    """)
    assert len(deleted_with_failed) == 0, (
        f"Deleted users with failed orders: {deleted_with_failed}"
    )