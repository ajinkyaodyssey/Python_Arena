# DAY 8 - FILE 3: Challenge
# Write all context managers from scratch
# Run with: python3 day8_challenge.py

import sqlite3
import time
import os
from contextlib import contextmanager


# =============================================
# CHALLENGE 1: ManagedDB class-based
# =============================================
# Write a class called ManagedDB that:
# __init__(self, db_path):
#   - stores self.db_path
#   - sets self.conn = None
#   - sets self.cursor = None
#   - sets self._queries_executed = 0  (counter)
#
# __enter__(self):
#   - opens sqlite3.connect(self.db_path)
#   - sets conn.row_factory = sqlite3.Row
#   - creates self.cursor from the connection
#   - returns self
#
# __exit__(self, exc_type, exc_val, exc_tb):
#   - if no exception: commits the transaction
#   - if exception: rolls back the transaction
#   - ALWAYS closes the connection (use try/finally inside __exit__)
#   - returns False (never suppress exceptions)
#
# execute(self, sql, params=()):
#   - increments self._queries_executed
#   - calls self.cursor.execute(sql, params)
#   - returns self.cursor
#
# fetchall(self):
#   - returns self.cursor.fetchall()
#
# fetchone(self):
#   - returns self.cursor.fetchone()
#
# query_count property:
#   - returns self._queries_executed

class ManagedDB:
    def __init__(self, db_path):
        self.db_path =  db_path
        self.conn = None
        self.cursor = None      # conn manages the database connection, while cursor executes SQL statements and retrieves results
        self._queries_executed = 0      #counter
        
    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
        finally:
            self.conn.close()   # guaranteed even if commit/rollback raises
            self.conn = None
            self.cursor = None
        return False
    
    def execute(self, sql, params = ()):
        self._queries_executed+=1
        self.cursor.execute(sql, params)
        return self.cursor
        
    def fetchall(self):
        return self.cursor.fetchall()
        
    def fetchone(self):
        return self.cursor.fetchone()
        
    @property
    def query_count(self):
        """returns self._queries_executed"""
        return self._queries_executed


# =============================================
# CHALLENGE 2: managed_timer using @contextmanager
# =============================================
# Write a context manager function called managed_timer that:
# - Takes label (str)
# - Records start time when entering
# - On exit, calculates elapsed time in milliseconds
# - Yields a dict: {"label": label, "elapsed_ms": None}
#   (the dict is populated AFTER the with block completes)
# - After the with block, sets elapsed_ms in that dict
# - Prints: "  [label] completed in X.XXms"
# - Works correctly on both normal exit and exception
#   (times and prints even if exception occurred)
#
# Usage:
#   with managed_timer("login test") as timing:
#       time.sleep(0.1)
#   print(timing["elapsed_ms"])  # ~100.0

@contextmanager
def managed_timer(label):
    timing = {}

    start = time.perf_counter()

    try:
        yield timing
    finally:
        elapsed = (time.perf_counter() - start) * 1000

        timing["label"] = label
        timing["elapsed_ms"] = elapsed

        print(f"[{label}] completed in {elapsed:.2f}ms")

# =============================================
# CHALLENGE 3: temp_file using @contextmanager
# =============================================
# Write a context manager function called temp_file that:
# - Takes filename (str), content (str)
# - Creates the file with the given content before the with block
# - Yields the filename (so caller can use it)
# - ALWAYS deletes the file after the with block exits
#   (even if an exception occurred inside)
# - If deletion fails (file already gone), silently ignore it
#
# Usage:
#   with temp_file("test_data.csv", "id,name\n1,Alice") as path:
#       with open(path) as f:
#           print(f.read())
#   # file is deleted here automatically

@contextmanager
def temp_file(filename, content):
    with open(filename, "w") as f:
        f.write(content)
    # file is closed here, THEN yield
    try:
        yield filename
    finally:
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass
        


# =============================================
# CHALLENGE 4: managed_transaction using class
# =============================================
# Write a class called managed_transaction that:
# - Takes conn (sqlite3 connection object)
# - __enter__: saves a savepoint using conn.execute("SAVEPOINT sp")
#              returns self
# - __exit__:
#     - if no exception: releases savepoint:
#       conn.execute("RELEASE SAVEPOINT sp")
#     - if exception: rolls back to savepoint:
#       conn.execute("ROLLBACK TO SAVEPOINT sp")
#       then returns False (let exception propagate)
#
# This allows nested transactions (savepoints inside a connection)

class managed_transaction:
    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        self.conn.execute("SAVEPOINT sp")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.conn.execute("RELEASE SAVEPOINT sp")
        else:
            self.conn.execute("ROLLBACK TO SAVEPOINT sp")
        return False


# =============================================
# DO NOT MODIFY BELOW THIS LINE
# =============================================

print("=== TESTING CONTEXT MANAGERS ===\n")

# --- Test 1: ManagedDB basic usage ---
with ManagedDB(":memory:") as db:
    db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT)")
    db.execute("INSERT INTO users VALUES (1, 'divya@test.com')")
    db.execute("INSERT INTO users VALUES (2, 'arjun@test.com')")
    db.execute("SELECT * FROM users")
    rows = db.fetchall()

assert len(rows) == 2, f"Test 1a: expected 2 rows, got {len(rows)}"
assert rows[0]["email"] == "divya@test.com", "Test 1b failed"
print("TEST 1 PASSED: ManagedDB basic usage")

# --- Test 2: ManagedDB query_count property ---
with ManagedDB(":memory:") as db:
    db.execute("CREATE TABLE t (id INTEGER)")
    db.execute("INSERT INTO t VALUES (1)")
    db.execute("INSERT INTO t VALUES (2)")
    db.execute("SELECT * FROM t")
    count = db.query_count

assert count == 4, f"Test 2a: expected 4 queries, got {count}"
print("TEST 2 PASSED: ManagedDB query_count property")

# --- Test 3: ManagedDB rollback on exception ---
initial_conn = sqlite3.connect(":memory:")
initial_conn.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT)")
initial_conn.commit()

try:
    with ManagedDB(":memory:") as db:
        db.execute("CREATE TABLE t2 (id INTEGER)")
        db.execute("INSERT INTO t2 VALUES (99)")
        raise ValueError("Forced failure")
except ValueError:
    pass
# We cannot check the rollback on :memory: after close,
# but we verify the exception propagated (not suppressed)
print("TEST 3 PASSED: ManagedDB propagates exception")

# --- Test 4: ManagedDB __exit__ returns False ---
suppressed = False
try:
    with ManagedDB(":memory:") as db:
        db.execute("CREATE TABLE t (id INTEGER)")
        raise RuntimeError("should propagate")
except RuntimeError:
    suppressed = False
except Exception:
    suppressed = True

assert suppressed == False, "Test 4a: ManagedDB must not suppress exceptions"
print("TEST 4 PASSED: ManagedDB does not suppress exceptions")

# --- Test 5: managed_timer basic ---
with managed_timer("test operation") as timing:
    time.sleep(0.05)

assert "elapsed_ms" in timing, "Test 5a: timing dict must have elapsed_ms"
assert timing["label"] == "test operation", "Test 5b: label not set"
assert timing["elapsed_ms"] >= 40, \
    f"Test 5c: expected >= 40ms, got {timing['elapsed_ms']}"
assert timing["elapsed_ms"] < 500, \
    f"Test 5d: seems too slow: {timing['elapsed_ms']}ms"
print("TEST 5 PASSED: managed_timer records elapsed time")

# --- Test 6: managed_timer works on exception ---
timing_result = {}
try:
    with managed_timer("failing op") as timing:
        time.sleep(0.02)
        raise ValueError("test error")
except ValueError:
    timing_result = timing

assert timing_result.get("elapsed_ms") is not None, \
    "Test 6a: elapsed_ms should be set even on exception"
assert timing_result["elapsed_ms"] >= 10, "Test 6b: should have recorded time"
print("TEST 6 PASSED: managed_timer works even when exception occurs")

# --- Test 7: temp_file creates and deletes ---
test_content = "id,name,status\n1,login,PASS\n2,checkout,FAIL"

with temp_file("test_data.csv", test_content) as path:
    assert path == "test_data.csv", "Test 7a: path should be the filename"
    assert os.path.exists(path), "Test 7b: file should exist inside with block"
    with open(path) as f:
        content = f.read()
    assert content == test_content, "Test 7c: file content should match"

assert not os.path.exists("test_data.csv"), \
    "Test 7d: file should be deleted after with block"
print("TEST 7 PASSED: temp_file creates and auto-deletes file")

# --- Test 8: temp_file deletes even on exception ---
try:
    with temp_file("temp_exception.csv", "data") as path:
        assert os.path.exists(path), "Test 8a: file should exist"
        raise RuntimeError("error inside with block")
except RuntimeError:
    pass

assert not os.path.exists("temp_exception.csv"), \
    "Test 8b: file must be deleted even when exception occurred"
print("TEST 8 PASSED: temp_file cleans up on exception")

# --- Test 9: managed_transaction commit ---
conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE data (val INTEGER)")
conn.commit()

with managed_transaction(conn):
    conn.execute("INSERT INTO data VALUES (42)")

cursor = conn.execute("SELECT * FROM data")
rows = cursor.fetchall()
assert len(rows) == 1, f"Test 9a: expected 1 row after commit, got {len(rows)}"
assert rows[0][0] == 42, "Test 9b: value should be 42"
print("TEST 9 PASSED: managed_transaction commits on success")

# --- Test 10: managed_transaction rollback ---
conn2 = sqlite3.connect(":memory:")
conn2.execute("CREATE TABLE data2 (val INTEGER)")
conn2.commit()

try:
    with managed_transaction(conn2):
        conn2.execute("INSERT INTO data2 VALUES (99)")
        raise ValueError("rollback this")
except ValueError:
    pass

cursor2 = conn2.execute("SELECT * FROM data2")
rows2 = cursor2.fetchall()
assert len(rows2) == 0, \
    f"Test 10a: expected 0 rows after rollback, got {len(rows2)}"
print("TEST 10 PASSED: managed_transaction rolls back on exception")

conn.close()
conn2.close()

print("\nALL 10 TESTS PASSED. Day 8 complete.")