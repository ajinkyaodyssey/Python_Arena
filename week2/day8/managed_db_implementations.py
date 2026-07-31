# DAY 8 - FILE 2: ManagedDB - Two Ways
# Run with: python3 managed_db_implementations.py

import sqlite3
from contextlib import contextmanager


# =============================================
# SECTION 1: ManagedDB using __enter__ / __exit__
# =============================================


# The class based approach.
# More verbose but gives you full control over every step.
# Use when you need complex state management or multiple methods.

print("=== MANAGEDDB: CLASS-BASED ===")

class ManagedDB:
    """
    Context manager for SQLite database connections.
    Guarantees:
    - Connection is always opened before Use
    - Transaction is commited on success
    - Transaction is rolled back on any exception
    - Connection is always closed, no matter what
    """
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def __enter__(self):
        print(f" [DB] Opening connection to {self.db_path}")
        self.conn = sqlite3.connect(self.db_path)   # Creates a connection to the SQLite database using the database path and stores the connection object in self.conn for executing SQL queries
        self.conn.row_factory = sqlite3.Row         # rows behave like dicts
        self.cursor = self.conn.cursor()
        print(f" [DB] Connection opened")
        return self             # 'as db' receives this object
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # No exception - commit the transaction
            print(f" [DB] Success - commiting transaction")
            self.conn.commit()      # Save all the changes I've made to the database permanently
        else:
            # Exception occured - rollback everything
            print(f" [DB] Exception {exc_type.__name__} - rolling back")
            self.conn.rollback()
        
        # Always close the Connection
        print(f" [DB] Closing connection")
        self.conn.close()
        self.conn = None 
        self.cursor = None 
        
        return False        #Never suppress execptions
        
    def execute(self, sql, params=()):
        return self.cursor.execute(sql, params)
        
    def fetchall(self):
        return self.cursor.fetchall()
        
    def fetchone(self):
        return self.cursor.fetchone()
        

# --- Usage: success path ---
print("--- Success path ---")
with ManagedDB(":memory:") as db:
    db.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            role TEXT DEFAULT 'tester'
        )
    """)
    db.execute("INSERT INTO users VALUES (1, 'divya@test.com', 'sdet')")
    db.execute("INSERT INTO users VALUES (2, 'arjun@test.com', 'admin')")
    rows = db.fetchall()
    # note: fetchall after INSERT returns nothing
    db.execute("SELECT * FROM users")
    rows = db.fetchall()
    print(f"  Inserted {len(rows)} users")
    for row in rows:
        print(f"    {row['id']}: {row['email']} ({row['role']})")
print("  Connection closed after with block\n")

# --- Usage: exception path (rollback) ---
print("--- Exception path (rollback) ---")
try:
    with ManagedDB(":memory:") as db:
        db.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT)")
        db.execute("INSERT INTO items VALUES (1, 'backpack')")
        print("  Inserted backpack")
        raise ValueError("Simulating a test failure mid-transaction")
        db.execute("INSERT INTO items VALUES (2, 'bike light')")  # never runs
except ValueError as e:
    print(f"  Caught exception: {e}")
    print("  Rollback happened - no data persisted")
    
    
# =============================================
# SECTION 2: ManagedDB using @contextmanager
# =============================================


# The generator-based approach.
# Less verbose. yield replaces __enter__/__exit__.
# Code before yield = __enter__
# Code after yield  = __exit__
# try/finally guarantees cleanup

print("\n=== MANAGEDDB: @CONTEXTMANAGER ===")

@contextmanager
def managed_db(db_path):
    """
    Same behaviour as the class above, using @contextmanager.
    Everything before yield = setup (__enter__)
    The yield value      = what 'as' receives
    Everything after yield = teardown (__exit__)
    finally = runs whether or not an exception occurred
    """
    print(f" [DB] Opening connection to {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn       # 'as conn' in the with statement receives this
        # If we reach here, no exception occurred
        print(f" [DB] Success - committing")
        conn.commit()
    except Exception as e:
        print(f" [DB] Exception {type(e).__name__} - rolling back")
        conn.rollback()
        raise       # re-raise - don't suppress
    finally:
        print(f" [DB] Closing connection")
        conn.close()        #ALWAYS runs - this is why finally matters
        
# --- Usage: identical to class-based ---
print("--- Success path ---")
with managed_db(":memory:") as conn:
    conn.execute("""
        CREATE TABLE tests (
            id INTEGER PRIMARY KEY,
            name TEXT,
            status TEXT
        )
    """)
    conn.execute("INSERT INTO tests VALUES (1, 'login_test', 'PASS')")
    conn.execute("INSERT INTO tests VALUES (2, 'checkout_test', 'FAIL')")
    cursor = conn.execute("SELECT * FROM tests WHERE status = 'PASS'")
    rows = cursor.fetchall()
    print(f"  Passing tests: {[dict(r) for r in rows]}")
    
print("\n--- Exception path (rollback) ---")
try:
    with managed_db(":memory:") as conn:
        conn.execute("CREATE TABLE data (id INTEGER)")
        conn.execute("INSERT INTO data VALUES (1)")
        raise RuntimeError("Something broke")
except RuntimeError as e:
    print(f"  Caught: {e}")
    

# =============================================
# SECTION 3: Why @contextmanager finally matters
# =============================================


print("\n=== WHY FINALLY MATTERS IN @CONTEXTMANAGER ===")

# WRONG: without finally, cleanup skipped on exception

@contextmanager
def bad_managed_db(db_path):
    conn = sqlite3.connect(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    # BUG: conn.close() is here, NOT in finally
    con.close()     # if exception was raised and re-raised, this NEVER runs
    print("  [bad] connection closed")  # also never runs on exception

# CORRECT: finally guarantees close() always runs
@contextmanager
def good_managed_db(db_path):
    conn = sqlite3.connect(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()            # runs on success AND on exception
        print("  [good] connection always closed")
        
print("--- bad_managed_db on exception ---")
try:
    with bad_managed_db(":memory:") as conn:
        raise RuntimeError("test")
except RuntimeError:
    print("  bad: connection was NEVER closed")  # leaked!

print("\n--- good_managed_db on exception ---")
try:
    with good_managed_db(":memory:") as conn:
        raise RuntimeError("test")
except RuntimeError:
    print("  good: connection was properly closed")


# =============================================
# SECTION 4: Class-based vs @contextmanager
# =============================================


print("\n=== WHEN TO USE WHICH ===")

print("""
Use CLASS-BASED (__enter__/__exit__) when:
  - You need the context manager to have its own methods
    Example: db.execute(), db.fetchall() on the manager itself
  - You need to store state across multiple operations
  - Multiple with statements reuse the same instance
  - You are writing a library that others will use

Use @CONTEXTMANAGER when:
  - Simple setup + teardown with no extra methods needed
  - One-off context managers
  - You want readable, compact code
  - The resource is handed directly to the caller (yield conn vs yield self)

Both guarantee cleanup. Choose based on complexity.
""")


# =============================================
# SECTION 5: Nested context managers
# =============================================


print("=== NESTED CONTEXT MANAGERS ===")

@contextmanager
def timer(label):
    import time
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"  [{label}] took {elapsed:.4f}s")

@contextmanager
def log_section(name):
    print(f"  --- {name} START ---")
    try:
        yield
    finally:
        print(f"  --- {name} END ---")

# Nest them
with timer("total"), log_section("DB operations"):
    with managed_db(":memory:") as conn:
        conn.execute("CREATE TABLE x (id INTEGER)")
        conn.execute("INSERT INTO x VALUES (42)")
        cursor = conn.execute("SELECT * FROM x")
        print(f"  Result: {cursor.fetchone()[0]}")

# One-liner nested (same as above)
# with timer("t"), log_section("s"), managed_db(":memory:") as conn: