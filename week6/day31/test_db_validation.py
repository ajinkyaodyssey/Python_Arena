# week6/day31/test_db_validation.py
# 10 DB validation tests covering real SDET scenarios.
# These are the tests you write AFTER an API or UI action
# to verify the database state is correct.
# Run with: pytest week6/day31/test_db_validation.py -v

import pytest
import sqlite3
from week6.day31.db_helpers import (
    fetch_all, fetch_one, fetch_value,
    execute, user_exists, order_exists,
    get_user, get_orders_for_user, count_rows
)


# =============================================
# TEST 1: Total record counts are as expected
# =============================================
# Use case: after a bulk import test, verify
# exactly N records were created — no more, no less.

def test_total_user_count_matches_expected(db):
    """
    After seeding test data, verify exact row count.
    Catches: duplicate inserts, missing records,
    partial failures in bulk operations.
    """
    count = fetch_value("SELECT COUNT(*) FROM users")

    assert count == 10, (
        f"Expected 10 users in test DB, got {count}. "
        f"Check if test data was seeded correctly."
    )


def test_total_order_count_matches_expected(db):
    """Verify order count after test data seed."""
    count = fetch_value("SELECT COUNT(*) FROM orders")

    assert count == 10, (
        f"Expected 10 orders, got {count}."
    )


# =============================================
# TEST 2: Specific record exists with correct values
# =============================================
# Use case: after POST /users, verify the user
# was actually created with the right field values.

def test_user_record_has_correct_field_values(db):
    """
    Simulate: POST /users created user with id=1.
    Verify every field was stored correctly.
    This catches field mapping bugs where the API
    accepts data but stores it in the wrong column.
    """
    user = get_user(1)

    assert user is not None, "User with id=1 should exist"
    assert user["name"] == "Divya Kumar", (
        f"Expected 'Divya Kumar', got '{user['name']}'"
    )
    assert user["email"] == "divya@test.com", (
        f"Expected 'divya@test.com', got '{user['email']}'"
    )
    assert user["role"] == "sdet"
    assert user["status"] == "active"
    assert user["age"] == 28


def test_order_record_has_correct_amount(db):
    """
    Simulate: POST /orders created an order.
    Verify amount was stored exactly — not rounded,
    not truncated, not converted to wrong currency.
    Amount bugs are silent and catastrophic in production.
    """
    order = fetch_one(
        "SELECT * FROM orders WHERE id = ?", (1,)
    )

    assert order is not None, "Order with id=1 should exist"
    assert order["amount"] == 2999.00, (
        f"Expected 2999.00, got {order['amount']}. "
        f"Possible float precision or currency bug."
    )
    assert order["status"] == "completed"
    assert order["user_id"] == 1


# =============================================
# TEST 3: Data integrity — no orphaned records
# =============================================
# Use case: verify all orders belong to real users.
# Orphaned records = referential integrity violation.

def test_no_orphaned_orders(db):
    """
    Every order.user_id must reference an existing user.
    Orphaned orders indicate:
    - User was deleted but orders were not cleaned up
    - Order was created with invalid user_id
    - Cascade delete is not configured correctly
    """
    orphaned = fetch_all("""
        SELECT o.id, o.user_id, o.product
        FROM orders o
        LEFT JOIN users u ON o.user_id = u.id
        WHERE u.id IS NULL
    """)

    assert len(orphaned) == 0, (
        f"Found {len(orphaned)} orphaned orders "
        f"with no matching user: "
        f"{[o['product'] for o in orphaned]}"
    )


# =============================================
# TEST 4: NULL / missing data validation
# =============================================
# Use case: verify required fields are never NULL.
# NULL in required fields = incomplete registration bug.

def test_no_active_users_have_null_email(db):
    """
    Business rule: active users must have an email.
    Email is required for notifications and login.
    A NULL email on an active user = broken registration flow.
    """
    null_emails = fetch_all("""
        SELECT id, name FROM users
        WHERE status = 'active'
        AND email IS NULL
    """)

    assert len(null_emails) == 0, (
        f"Active users with NULL email found: "
        f"{[u['name'] for u in null_emails]}. "
        f"Registration flow may have a bug."
    )


def test_all_orders_have_positive_amount(db):
    """
    No order should have zero or negative amount.
    Zero amount = free order bug.
    Negative amount = refund stored as order bug.
    """
    bad_amounts = fetch_all("""
        SELECT id, product, amount FROM orders
        WHERE amount <= 0
    """)

    assert len(bad_amounts) == 0, (
        f"Orders with invalid amount: "
        f"{[(o['product'], o['amount']) for o in bad_amounts]}"
    )


# =============================================
# TEST 5: Business rule validation
# =============================================
# Use case: verify business logic was applied
# correctly when data was saved.

def test_deleted_users_have_no_active_orders(db):
    """
    Business rule: when a user is deleted,
    their pending/active orders should be cancelled.
    Deleted user with pending order = broken delete flow.
    """
    violations = fetch_all("""
        SELECT u.name, u.status, o.product, o.status as order_status
        FROM users u
        INNER JOIN orders o ON u.id = o.user_id
        WHERE u.status = 'deleted'
        AND o.status IN ('pending', 'active')
    """)

    assert len(violations) == 0, (
        f"Deleted users with active/pending orders: "
        f"{[(v['name'], v['order_status']) for v in violations]}"
    )


def test_completed_orders_have_valid_user_email(db):
    """
    Every completed order must have a user with a valid email.
    We need to send confirmation emails for completed orders.
    No email = cannot notify customer = support ticket waiting to happen.
    """
    no_email = fetch_all("""
        SELECT u.name, o.product
        FROM orders o
        INNER JOIN users u ON o.user_id = u.id
        WHERE o.status = 'completed'
        AND u.email IS NULL
    """)

    assert len(no_email) == 0, (
        f"Completed orders with unreachable users: "
        f"{[(r['name'], r['product']) for r in no_email]}"
    )


# =============================================
# TEST 6: Aggregate validation
# =============================================
# Use case: after payment tests verify financials.

def test_total_completed_revenue_is_positive(db):
    """
    Sum of all completed order amounts must be positive.
    Zero or negative = payment processing bug.
    """
    total = fetch_value("""
        SELECT SUM(amount) FROM orders
        WHERE status = 'completed'
    """)

    assert total is not None, "Should have completed orders"
    assert total > 0, (
        f"Total completed revenue is {total} — "
        f"expected positive value."
    )
    print(f"\n  Total completed revenue: ₹{total:,.2f}")


def test_average_order_amount_is_within_expected_range(db):
    """
    Average order should be between ₹500 and ₹10,000.
    Outside this range suggests data corruption or
    test data was not cleaned up between runs.
    """
    avg = fetch_value("SELECT AVG(amount) FROM orders")

    assert avg is not None
    assert 500 <= avg <= 10000, (
        f"Average order amount ₹{avg:.2f} is outside "
        f"expected range ₹500–₹10,000. "
        f"Check if test data is clean."
    )
    print(f"\n  Average order amount: ₹{avg:.2f}")


# =============================================
# TEST 7: Write + verify pattern
# =============================================
# Use case: simulate what happens after an API
# creates a record. Insert it, verify it exists,
# cleanup automatically via conftest fixture.

def test_insert_user_and_verify_it_exists(db_write):
    """
    Simulates the full API create flow at DB level:
    1. INSERT a user (simulating what POST /users does to DB)
    2. Verify it exists with correct values
    3. Fixture cleans it up automatically after test

    In a real framework this would be:
    1. Call POST /users via requests
    2. Extract the id from response
    3. Query DB to verify the row was created correctly
    """
    conn, inserted_ids = db_write

    # Simulate what POST /users does to the database
    conn.execute("""
        INSERT INTO users (id, name, email, role, status, created_at, age)
        VALUES (99, 'Test User API', 'testapi@test.com',
                'sdet', 'active', '2024-11-01', 25)
    """)
    conn.commit()
    inserted_ids["users"].append(99)

    # Now verify the record exists with correct values
    # (this is what you do after an API test)
    cursor = conn.execute(
        "SELECT * FROM users WHERE id = ?", (99,)
    )
    user = dict(cursor.fetchone())

    assert user["name"] == "Test User API"
    assert user["email"] == "testapi@test.com"
    assert user["role"] == "sdet"
    assert user["status"] == "active"
    print(f"\n  Inserted and verified: {user['name']}")
    # Fixture automatically deletes user id=99 after this test


# =============================================
# TEST 8: Duplicate detection
# =============================================
# Use case: after running a create test multiple times,
# verify no duplicate records were created.

def test_no_duplicate_emails_in_users(db):
    """
    Each email should appear at most once.
    Duplicates indicate:
    - Missing unique constraint on email column
    - API allows creating same user twice
    - Race condition in concurrent test runs
    """
    duplicates = fetch_all("""
        SELECT email, COUNT(*) AS occurrences
        FROM users
        WHERE email IS NOT NULL
        GROUP BY email
        HAVING COUNT(*) > 1
    """)

    assert len(duplicates) == 0, (
        f"Duplicate emails found: "
        f"{[(d['email'], d['occurrences']) for d in duplicates]}"
    )


# =============================================
# TEST 9: Pagination data integrity
# =============================================
# Use case: after GET /users?page=1&per_page=5
# verify the DB actually has the right number
# of records to paginate correctly.

def test_user_count_supports_expected_pagination(db):
    """
    If the API says there are 2 pages of 5 users each,
    the DB must actually have 10 users.
    Mismatch = pagination metadata is wrong.
    """
    total_users = fetch_value("SELECT COUNT(*) FROM users")
    per_page = 5
    expected_pages = -(-total_users // per_page)  # ceiling division

    assert total_users == 10, (
        f"Expected 10 users for 2-page pagination, got {total_users}"
    )
    assert expected_pages == 2, (
        f"Expected 2 pages with per_page=5, "
        f"got {expected_pages} pages for {total_users} users"
    )
    print(
        f"\n  {total_users} users = "
        f"{expected_pages} pages at {per_page} per page"
    )


# =============================================
# TEST 10: Cross-table consistency
# =============================================
# Use case: verify data is consistent across
# multiple tables — what the users table says
# must match what the orders table shows.

def test_user_order_counts_are_consistent(db):
    """
    The number of orders per user in the orders table
    must be consistent — no user should have orders
    that reference a non-existent user_id.

    This catches foreign key violations that happen when:
    - Users are deleted without cascade to orders
    - Orders are imported with wrong user_id mapping
    - Test data setup was incomplete
    """
    # Get all user_ids that appear in orders
    order_user_ids = fetch_all(
        "SELECT DISTINCT user_id FROM orders"
    )
    order_user_id_set = {r["user_id"] for r in order_user_ids}

    # Get all actual user ids
    all_user_ids = fetch_all("SELECT id FROM users")
    all_user_id_set = {r["id"] for r in all_user_ids}

    # Every user_id in orders must exist in users
    orphaned_user_ids = order_user_id_set - all_user_id_set

    assert len(orphaned_user_ids) == 0, (
        f"Orders reference user_ids that don't exist: "
        f"{orphaned_user_ids}. "
        f"Foreign key integrity violated."
    )
    print(
        f"\n  All {len(order_user_id_set)} user_ids "
        f"in orders exist in users table"
    )