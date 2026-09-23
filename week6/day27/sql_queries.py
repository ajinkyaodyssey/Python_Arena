# week6/day27/sql_queries.py
# SQL queries from Python — how you validate DB state in tests
# Run with: python3 sql_queries.py

import sqlite3
import os

DB_PATH = "test_db.db"


def get_connection():
    """Create connection with row_factory so rows behave like dicts."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def run_query(sql: str, params: tuple = ()) -> list:
    """Run a SELECT query and return list of row dicts."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]


# =============================================
# THE QUERIES — each one is a real test assertion
# =============================================

print("=" * 50)
print("SQL QUERY PRACTICE")
print("=" * 50)

# 1. Count all active users
active_users = run_query(
    "SELECT COUNT(*) AS count FROM users WHERE status = 'active'"
)
print(f"\n1. Active users: {active_users[0]['count']}")
#########FLOW#########
# SQLite executes
#     ↓
# count = 73
#     ↓
# dict(row)
#     ↓
# {"count": 73}
#     ↓
# list comprehension
#     ↓
# [{"count": 73}]
#     ↓
# active_users
#     ↓
# active_users[0]
#     ↓
# {"count": 73}
#     ↓
# ['count']
#     ↓
# 73
######################

# 2. Find users with no email (data quality bug)
no_email = run_query("SELECT id, name FROM users WHERE email IS NULL")
print(f"\n2. Users with no email: {len(no_email)}")
for u in no_email:
    print(f"   ID {u['id']}: {u['name']}")

# 3. All SDET users sorted by name
sdets = run_query(
    "SELECT name, email FROM users WHERE role = ? ORDER BY name ASC",
    ("sdet",)
)
print(f"\n3. SDET users ({len(sdets)}):")
for s in sdets:
    print(f"   {s['name']} — {s['email']}")

# 4. Top 3 most expensive orders
top_orders = run_query(
    """SELECT product, amount, status
       FROM orders
       ORDER BY amount DESC
       LIMIT 3"""
)
print("\n4. Top 3 most expensive orders:")
for o in top_orders:
    print(f"   {o['product']}: ₹{o['amount']} ({o['status']})")

# 5. Failed or pending orders
problem_orders = run_query(
    "SELECT * FROM orders WHERE status IN (?, ?)",
    ("failed", "pending")
)
print(f"\n5. Problem orders (failed + pending): {len(problem_orders)}")

# 6. Orders between 1000 and 3000
mid_range = run_query(
    "SELECT product, amount FROM orders WHERE amount BETWEEN ? AND ?",
    (1000, 3000)
)
print(f"\n6. Orders ₹1000–₹3000: {len(mid_range)}")

# 7. Test email accounts
test_accounts = run_query(
    "SELECT name, email FROM users WHERE email LIKE '%@test.com'"
)
print(f"\n7. Test accounts: {len(test_accounts)}")
for t in test_accounts:
    print(f"   {t['name']}: {t['email']}")

# 8. Users aged 25-30
young_users = run_query(
    "SELECT name, age FROM users WHERE age BETWEEN ? AND ? ORDER BY age",
    (25, 30)
)
print(f"\n8. Users aged 25-30: {len(young_users)}")
for u in young_users:
    print(f"   {u['name']}: {u['age']}")

# 9. Non-deleted users with email
valid_users = run_query(
    """SELECT name, email FROM users
       WHERE status != 'deleted'
       AND email IS NOT NULL
       ORDER BY name"""
)
print(f"\n9. Valid users (not deleted, has email): {len(valid_users)}")

# 10. Most recent 5 orders
recent = run_query(
    "SELECT product, created_at FROM orders ORDER BY created_at DESC LIMIT 5"
)
print("\n10. Most recent 5 orders:")
for r in recent:
    print(f"   {r['created_at']}: {r['product']}")

print("\n" + "=" * 50)
print("ALL QUERIES COMPLETE")
print("=" * 50)