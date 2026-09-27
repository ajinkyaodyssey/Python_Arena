# week6/day29/grouping_queries.py
# 5 grouping problems — real SDET use cases
# Run with: python3 grouping_queries.py

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "test_db.db")


def query(sql: str, params: tuple = ()) -> list:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]


print("=" * 55)
print("5 GROUPING PROBLEMS — SDET USE CASES")
print("=" * 55)


# =============================================
# PROBLEM 1
# "How many users do we have per role?
#  Are roles distributed as expected?"
# =============================================
print("\n--- PROBLEM 1: User count by role ---")
print("Question: How many users per role?")

result = query("""
    SELECT
        role,
        COUNT(*) AS total,
        COUNT(CASE WHEN status = 'active' THEN 1 END) AS active,
        COUNT(CASE WHEN status != 'active' THEN 1 END) AS inactive
    FROM users
    GROUP BY role
    ORDER BY total DESC
""")

for r in result:
    print(
        f"  {r['role']:8} | total: {r['total']} | "
        f"active: {r['active']} | inactive: {r['inactive']}"
    )

assert len(result) > 0, "Should have at least one role"
print(f"  ✓ Found {len(result)} distinct roles")


# =============================================
# PROBLEM 2
# "What is the revenue breakdown by order status?
#  Which status has the most money?"
# =============================================
print("\n--- PROBLEM 2: Revenue by order status ---")
print("Question: How much money per status?")

result = query("""
    SELECT
        status,
        COUNT(*) AS order_count,
        SUM(amount) AS total_revenue,
        AVG(amount) AS avg_amount,
        MAX(amount) AS max_amount
    FROM orders
    GROUP BY status
    ORDER BY total_revenue DESC
""")

for r in result:
    print(
        f"  {r['status']:12} | "
        f"count: {r['order_count']} | "
        f"total: ₹{r['total_revenue']:,.2f} | "
        f"avg: ₹{r['avg_amount']:,.2f}"
    )

completed = next((r for r in result if r['status'] == 'completed'), None)
assert completed is not None, "Should have completed orders"
assert completed['total_revenue'] > 0, "Revenue must be positive"
print(f"  ✓ Completed orders revenue: ₹{completed['total_revenue']:,.2f}")


# =============================================
# PROBLEM 3
# "Which users are our biggest spenders?
#  Find users who spent more than 3000 total"
# =============================================
print("\n--- PROBLEM 3: High-value customers ---")
print("Question: Who spent more than ₹3000 total?")

result = query("""
    SELECT
        u.name,
        u.role,
        COUNT(o.id) AS order_count,
        SUM(o.amount) AS total_spent
    FROM users u
    INNER JOIN orders o ON u.id = o.user_id
    GROUP BY u.id, u.name, u.role
    HAVING SUM(o.amount) > 3000
    ORDER BY total_spent DESC
""")

for r in result:
    print(
        f"  {r['name']:15} | {r['role']:8} | "
        f"orders: {r['order_count']} | "
        f"spent: ₹{r['total_spent']:,.2f}"
    )

assert len(result) > 0, "Should have at least one high-value customer"
print(f"  ✓ Found {len(result)} high-value customers")


# =============================================
# PROBLEM 4
# "Data quality check: find roles where any user
#  has a missing email — signals incomplete registration"
# =============================================
print("\n--- PROBLEM 4: Data quality by role ---")
print("Question: Which roles have users with missing emails?")

result = query("""
    SELECT
        role,
        COUNT(*) AS total_users,
        COUNT(email) AS users_with_email,
        COUNT(*) - COUNT(email) AS missing_emails
    FROM users
    GROUP BY role
    HAVING COUNT(*) - COUNT(email) > 0
    ORDER BY missing_emails DESC
""")

if result:
    for r in result:
        print(
            f"  {r['role']:8} | "
            f"total: {r['total_users']} | "
            f"missing emails: {r['missing_emails']}"
        )
    print(f"  ⚠ {len(result)} role(s) have users with missing emails")
else:
    print("  ✓ All roles have complete email data")


# =============================================
# PROBLEM 5
# "After a test run: verify order counts per user
#  match what the test created.
#  Flag anyone with unexpected order count"
# =============================================
print("\n--- PROBLEM 5: Order count validation ---")
print("Question: How many orders does each user have?")
print("         Flag users with more than 2 orders (unexpected)")

result = query("""
    SELECT
        u.name,
        u.status,
        COUNT(o.id) AS order_count,
        COALESCE(SUM(o.amount), 0) AS total_amount
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    GROUP BY u.id, u.name, u.status
    ORDER BY order_count DESC, u.name
""")

unexpected = []
for r in result:
    flag = " ← CHECK THIS" if r['order_count'] > 2 else ""
    print(
        f"  {r['name']:15} | "
        f"orders: {r['order_count']} | "
        f"total: ₹{r['total_amount']:,.2f}{flag}"
    )
    if r['order_count'] > 2:
        unexpected.append(r['name'])

if unexpected:
    print(f"\n  ⚠ Users with >2 orders: {unexpected}")
else:
    print(f"\n  ✓ All users within expected order count")


print("\n" + "=" * 55)
print("ALL 5 PROBLEMS SOLVED")
print("=" * 55)