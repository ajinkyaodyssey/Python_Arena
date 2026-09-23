# week6/day27/test_db_validation.py
# DB validation using SQL inside pytest tests
# Run with: pytest week6/day27/test_db_validation.py -v

import pytest
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "test_db.db")


@pytest.fixture(scope="session")
def db():
    """Session-scoped database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def query(db, sql, params=()):
    """Helper: run query, return list of dicts."""
    return [dict(r) for r in db.execute(sql, params).fetchall()]


# =============================================
# DATA QUALITY TESTS
# =============================================

def test_no_users_have_null_email_except_known(db):
    """
    Business rule: all active users must have an email.
    Null emails are allowed only for inactive users.
    """
    null_active = query(
        db,
        "SELECT * FROM users WHERE email IS NULL AND status = 'active'"
    )
    assert len(null_active) == 0, (
        f"Active users with null email found: "
        f"{[u['name'] for u in null_active]}"
    )

#_______________________________________________________________________________

# pytest execution start
#    │
#    ├── 1. Setup Phase
#    │     └── pytest finds test_no_users_have_null_email_except_known(db)
#    │           └── Pytest sees "db" parameter ──► Calls db() fixture
#    │                                                 │
#    │                                                 ├─ sqlite3.connect(...)
#    │                                                 ├─ row_factory set
#    │                                                 └─ yield conn (Pauses fixture here)
#    │
#    ├── 2. Test Execution Phase
#    │     └── Passes 'conn' into the test as the 'db' argument
#    │           └── test_no_users_have_null_email_except_known(db) starts running
#    │                 │
#    │                 ├─ Calls query(db, "SELECT...")
#    │                 │     │
#    │                 │     ├─ Runs db.execute(...).fetchall()
#    │                 │     ├─ Converts sqlite3.Row items to dicts: [dict(r) ...]
#    │                 │     └─ Returns list of dicts to 'null_active'
#    │                 │
#    │                 └─ Executes assert len(null_active) == 0
#    │                       ├─ Passed? ──► Test succeeds
#    │                       └─ Failed? ──► Formats error message with [u['name'] ...]
#    │
#    └── 3. Teardown Phase
#          └── Test finishes/exits
#                └── pytest resumes db() fixture right after 'yield'
#                      └─ conn.close()

#_______________________________________________________________________________


def test_all_completed_orders_have_positive_amount(db):
    """
    Business rule: completed orders must have amount > 0.
    Zero or negative amounts on completed orders = billing bug.
    """
    bad_orders = query(
        db,
        "SELECT * FROM orders WHERE status = 'completed' AND amount <= 0"
    )
    assert len(bad_orders) == 0, (
        f"Completed orders with zero/negative amount: {bad_orders}"
    )


def test_deleted_users_count_is_within_expected_range(db):
    """
    Verify deletion rate is not unexpectedly high.
    Sudden spike in deleted users = possible bug or data corruption.
    """
    result = query(
        db,
        "SELECT COUNT(*) AS count FROM users WHERE status = 'deleted'"
    )
    deleted_count = result[0]["count"]
    total = query(db, "SELECT COUNT(*) AS count FROM users")[0]["count"]
    deletion_rate = deleted_count / total

    assert deletion_rate < 0.5, (
        f"Deletion rate {deletion_rate:.1%} is too high — "
        f"{deleted_count}/{total} users deleted"
    )
#______________________________________________________________________________________

# SQL
# ↓
# SELECT COUNT(*) AS count
# ↓
# Database result
# ↓
# count = 20
# ↓
# dict(r)
# ↓
# {"count": 20}
# ↓
# query() returns
# ↓
# [{"count": 20}]
# ↓
# result
# ↓
# result[0]
# ↓
# {"count": 20}
# ↓
# result[0]["count"]
# ↓
# 20
# ↓
# deleted_count
# ↓
# 20

#______________________________________________________________________________________

def test_most_expensive_order_is_correct(db):
    """
    Verify the highest value order matches expected data.
    Use case: after a payment test, confirm the right amount was stored.
    """
    result = query(
        db,
        "SELECT product, amount FROM orders ORDER BY amount DESC LIMIT 1"
    )
    top_order = result[0]

    assert top_order["amount"] == 5999.00, (
        f"Expected top order to be 5999, got {top_order['amount']}"
    )
    assert top_order["product"] == "Security Testing"


def test_active_sdet_users_all_have_emails(db):
    """
    Active SDET role users must all have valid email addresses.
    SDETs need emails for test notification system.
    """
    sdets_without_email = query(
        db,
        """SELECT name FROM users
           WHERE role = 'sdet'
           AND status = 'active'
           AND email IS NULL"""
    )
    assert len(sdets_without_email) == 0, (
        f"Active SDETs without email: "
        f"{[u['name'] for u in sdets_without_email]}"
    )