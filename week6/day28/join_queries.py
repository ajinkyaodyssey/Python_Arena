# week6/day28/join_queries.py
# JOIN queries from Python — real SDET use cases
# Run with: python3 join_queries.py

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "test_db.db")


def query(sql: str, params: tuple = ()) -> list:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]


print("=" * 55)
print("JOIN QUERIES — SDET USE CASES")
print("=" * 55)


# =============================================
# INNER JOIN QUERIES
# =============================================

print("\n--- INNER JOIN ---")

# 1. Each order with the user's name
orders_with_names = query("""
    SELECT u.name, o.product, o.amount, o.status
    FROM orders o
    INNER JOIN users u ON o.user_id = u.id
    ORDER BY o.amount DESC
""")
print(f"\n1. All orders with user names ({len(orders_with_names)}):")
for r in orders_with_names:
    print(f"   {r['name']:15} | {r['product']:25} | ₹{r['amount']:8.2f} | {r['status']}")


# 2. Only SDET users and their orders
sdet_orders = query("""
    SELECT u.name, u.role, o.product, o.amount
    FROM orders o
    INNER JOIN users u ON o.user_id = u.id
    WHERE u.role = 'sdet'
    ORDER BY o.amount DESC
""")
print(f"\n2. Orders by SDET users ({len(sdet_orders)}):")
for r in sdet_orders:
    print(f"   {r['name']:15} | {r['product']:25} | ₹{r['amount']:.2f}")


# 3. Completed orders where user has email (can send confirmation)
confirmable = query("""
    SELECT u.name, u.email, o.product, o.amount
    FROM orders o
    INNER JOIN users u ON o.user_id = u.id
    WHERE o.status = 'completed'
    AND u.email IS NOT NULL
    ORDER BY o.created_at DESC
""")
print(f"\n3. Completed orders with valid email ({len(confirmable)}):")
for r in confirmable:
    print(f"   {r['name']:15} | {r['email']:25} | {r['product']}")


# =============================================
# LEFT JOIN QUERIES
# =============================================

print("\n--- LEFT JOIN ---")

# 4. ALL users with their order count (even if zero)
user_order_counts = query("""
    SELECT
        u.name,
        u.role,
        COUNT(o.id) AS total_orders,
        COALESCE(SUM(o.amount), 0) AS total_spent
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    GROUP BY u.id, u.name, u.role
    ORDER BY total_spent DESC
""")
print(f"\n4. All users with order summary:")
for r in user_order_counts:
    print(
        f"   {r['name']:15} | {r['role']:8} | "
        f"orders: {r['total_orders']} | "
        f"spent: ₹{r['total_spent']:.2f}"
    )


# 5. Active users with their latest order
active_with_orders = query("""
    SELECT u.name, o.product, o.status, o.created_at
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    WHERE u.status = 'active'
    ORDER BY u.name, o.created_at DESC
""")
print(f"\n5. Active users and their orders:")
for r in active_with_orders:
    order_info = f"{r['product']} ({r['status']})" if r['product'] else "no orders"
    print(f"   {r['name']:15} | {order_info}")


# =============================================
# USERS WITH NO ORDERS
# =============================================

print("\n--- USERS WITH NO ORDERS ---")

# 6. The classic interview query
no_orders = query("""
    SELECT u.id, u.name, u.email, u.role
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    WHERE o.id IS NULL
""")
print(f"\n6. Users with NO orders ({len(no_orders)}):")
for r in no_orders:
    print(f"   ID {r['id']:2} | {r['name']:15} | {r['role']:8} | {r['email'] or 'no email'}")


# 7. Active users with no orders (need re-engagement)
active_no_orders = query("""
    SELECT u.name, u.email
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    WHERE o.id IS NULL
    AND u.status = 'active'
    AND u.email IS NOT NULL
""")
print(f"\n7. Active users with email but no orders (re-engagement list):")
for r in active_no_orders:
    print(f"   {r['name']:15} | {r['email']}")


print("\n" + "=" * 55)
print("ALL JOIN QUERIES COMPLETE")
print("=" * 55)