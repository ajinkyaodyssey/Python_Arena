# week6/day30/interview_problems.py
# 8 classic SQL interview problems from Python
# Run with: python3 interview_problems.py

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "test_db.db")


def query(sql, params=()):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(r) for r in conn.execute(sql, params).fetchall()]


print("=" * 60)
print("8 CLASSIC SQL INTERVIEW PROBLEMS")
print("=" * 60)


# Problem 1: Second highest order amount
print("\n1. Second highest order amount:")
result = query("""
    SELECT MAX(amount) AS second_highest
    FROM orders
    WHERE amount < (SELECT MAX(amount) FROM orders)
""")
print(f"   ₹{result[0]['second_highest']:,.2f}")


# Problem 2: Users with more than one order
print("\n2. Users with more than 1 order:")
result = query("""
    SELECT u.name, COUNT(o.id) AS order_count
    FROM users u
    INNER JOIN orders o ON u.id = o.user_id
    GROUP BY u.id, u.name
    HAVING COUNT(o.id) > 1
    ORDER BY order_count DESC
""")
for r in result:
    print(f"   {r['name']}: {r['order_count']} orders")


# Problem 3: Users with NO orders
print("\n3. Users with no orders:")
result = query("""
    SELECT u.name, u.role
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    WHERE o.id IS NULL
""")
for r in result:
    print(f"   {r['name']} ({r['role']})")


# Problem 4: Duplicate emails (insert then remove)
print("\n4. Duplicate emails:")
with sqlite3.connect(DB_PATH) as conn:
    conn.execute("""
        INSERT INTO users VALUES
        (11,'Duplicate Test','divya@test.com','sdet','active','2024-11-01',25)
    """)
result = query("""
    SELECT email, COUNT(*) AS occurrences
    FROM users
    WHERE email IS NOT NULL
    GROUP BY email
    HAVING COUNT(*) > 1
""")
for r in result:
    print(f"   {r['email']}: {r['occurrences']} times")
with sqlite3.connect(DB_PATH) as conn:
    conn.execute("DELETE FROM users WHERE id = 11")


# Problem 5: Orders above average amount
print("\n5. Orders above average:")
result = query("""
    SELECT u.name, o.product, o.amount
    FROM orders o
    INNER JOIN users u ON o.user_id = u.id
    WHERE o.amount > (SELECT AVG(amount) FROM orders)
    ORDER BY o.amount DESC
""")
avg = query("SELECT ROUND(AVG(amount),2) AS a FROM orders")[0]["a"]
print(f"   Average: ₹{avg}")
for r in result:
    print(f"   {r['name']}: {r['product']} — ₹{r['amount']:,.2f}")


# Problem 6: Most recent order per user
print("\n6. Most recent order per user:")
result = query("""
    SELECT u.name, o.product, o.created_at
    FROM orders o
    INNER JOIN users u ON o.user_id = u.id
    WHERE o.created_at = (
        SELECT MAX(o2.created_at)
        FROM orders o2
        WHERE o2.user_id = o.user_id
    )
    ORDER BY u.name
""")
for r in result:
    print(f"   {r['name']}: {r['product']} ({r['created_at']})")


# Problem 7: Revenue by role
print("\n7. Total revenue per role:")
result = query("""
    SELECT u.role, SUM(o.amount) AS total, COUNT(o.id) AS orders
    FROM users u
    INNER JOIN orders o ON u.id = o.user_id
    GROUP BY u.role
    ORDER BY total DESC
""")
for r in result:
    print(f"   {r['role']:8}: ₹{r['total']:,.2f} ({r['orders']} orders)")


# Problem 8: Running total
print("\n8. Running total of orders by date:")
result = query("""
    SELECT
        created_at,
        amount,
        SUM(amount) OVER (
            ORDER BY created_at
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS running_total
    FROM orders
    ORDER BY created_at
""")
for r in result:
    print(
        f"   {r['created_at']}: "
        f"₹{r['amount']:,.2f} "
        f"→ running: ₹{r['running_total']:,.2f}"
    )

print("\n" + "=" * 60)
print("ALL 8 PROBLEMS COMPLETE")
print("=" * 60)