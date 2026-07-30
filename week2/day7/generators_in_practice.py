# DAY 7 - FILE 2: Generators in Real Test Automation Scenarios
# Run with: python3 generators_in_practice.py

import time
import json
import os

# =============================================
# SECTION 1: Paginated API reader generator
# =============================================
# Real APIs return data in pages.
# GET /users?page=1&per_page=10 -> 10 users
# GET /users?page=2&per_page=10 -> 10 more
# Without generator: fetch ALL pages, store ALL data, then process
# With generator: fetch one page, yield its items, fetch next page, repeat

print("=== PAGINATED API READER ===")

# Simulated API responses (in real code this would call requests.get())
def mock_api_get(endpoint, params):
    """Simulates a paginated API. Returns fake data."""
    page = params.get("page", 1)
    per_page = params.get("per_page", 5)
    total_items = 23    # total records in the fake database

    start_id = (page - 1) * per_page + 1
    end_id = min(start_id + per_page, total_items + 1)

    items = [
        {"id": i, "name": f"User {i}", "email": f"user{i}@test.com"}
        for i in range(start_id, end_id)
    ]

    total_pages = (total_items + per_page - 1) // per_page
    return {
        "data": items,
        "meta": {
            "page": page,
            "per_page": per_page,
            "total": total_items,
            "total_pages": total_pages
        }
    }


def paginated_reader(endpoint, per_page=5):
    """
    Generator that yields one item at a time from a paginated API.
    Fetches next page only when the current page is exhausted.
    Caller never sees pagination — just a stream of items.
    """
    page = 1
    while True:
        response = mock_api_get(endpoint, {"page": page, "per_page": per_page})
        data = response["data"]
        meta = response["meta"]

        print(f"  [API] Fetched page {page}/{meta['total_pages']} "
              f"({len(data)} items)")

        for item in data:
            yield item          # yield one item at a time to the caller

        # Check if there are more pages
        if page >= meta["total_pages"]:
            print(f"  [API] All pages fetched. Total items: {meta['total']}")
            return             # StopIteration - generator done

        page += 1


# Usage - caller sees a flat stream, not pages
print("All users:")
for user in paginated_reader("/users", per_page=5):
    print(f"  {user['id']}: {user['name']}")

# Find first user matching a condition - stops early, doesn't fetch all pages
print("\nFirst user with id > 18:")
for user in paginated_reader("/users", per_page=5):
    if user["id"] > 18:
        print(f"  Found: {user}")
        break               # generator pauses here - remaining pages never fetched

# =============================================
# SECTION 2: Log file parser using yield
# =============================================

print("\n=== LOG FILE PARSER ===")

# Create a sample log file
sample_log = """2024-01-15 10:00:01 INFO  TestRunner - Starting test suite: smoke
2024-01-15 10:00:02 INFO  LoginTest - Navigating to https://saucedemo.com
2024-01-15 10:00:03 DEBUG LoginTest - Filling username: standard_user
2024-01-15 10:00:04 INFO  LoginTest - Login successful
2024-01-15 10:00:05 ERROR CheckoutTest - Element #checkout-btn not found
2024-01-15 10:00:06 INFO  CheckoutTest - Retrying after 1s
2024-01-15 10:00:07 ERROR CheckoutTest - Timeout waiting for element
2024-01-15 10:00:08 INFO  SearchTest - Searching for: backpack
2024-01-15 10:00:09 WARNING SearchTest - Response time 1823ms exceeds threshold
2024-01-15 10:00:10 INFO  SearchTest - Found 3 results
2024-01-15 10:00:11 ERROR APITest - Connection refused: https://api.saucedemo.com
2024-01-15 10:00:12 INFO  TestRunner - Suite complete: 2 passed, 2 failed
"""

# Write the log file
with open("test_run.log", "w") as f:
    f.write(sample_log)


def read_log_lines(filepath):
    """
    Generator: reads a log file one line at a time.
    Never loads the entire file into memory.
    Works for 10-line files and 10GB files identically.
    """
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if line:            # skip empty lines
                yield line


def parse_log_entry(line):
    """Parse a single log line into a structured dict."""
    parts = line.split(" ", 4)
    if len(parts) < 5:
        return None
    return {
        "date": parts[0],
        "time": parts[1],
        "level": parts[2],
        "source": parts[3].rstrip(" -"),
        "message": parts[4].strip()
    }


def filter_by_level(log_generator, level):
    """
    Generator that filters another generator.
    This is a generator PIPELINE - no data stored anywhere.
    """
    for line in log_generator:
        entry = parse_log_entry(line)
        if entry and entry["level"] == level:
            yield entry


def filter_by_source(log_generator, source):
    """Another filter generator - can be chained."""
    for line in log_generator:
        entry = parse_log_entry(line) if isinstance(line, str) else line
        if entry and source in entry.get("source", ""):
            yield entry


# Basic usage: read and parse all lines
print("All log entries:")
for line in read_log_lines("test_run.log"):
    entry = parse_log_entry(line)
    if entry:
        print(f"  [{entry['level']}] {entry['source']}: {entry['message'][:50]}")

# Filter only errors - generator pipeline
print("\nERROR entries only:")
error_logs = filter_by_level(read_log_lines("test_run.log"), "ERROR")
for entry in error_logs:
    print(f"  {entry['time']} | {entry['source']} | {entry['message']}")

# Count errors without storing them all
error_count = sum(
    1 for line in read_log_lines("test_run.log")
    if "ERROR" in line
)
print(f"\nTotal errors: {error_count}")

# Find first error - stops reading at first match
print("\nFirst error found:")
for line in read_log_lines("test_run.log"):
    entry = parse_log_entry(line)
    if entry and entry["level"] == "ERROR":
        print(f"  {entry}")
        break

# =============================================
# SECTION 3: Generator pipeline
# =============================================

print("\n=== GENERATOR PIPELINE ===")

# Chain generators together - each transforms the stream
# No intermediate lists - data flows through one item at a time

def read_lines(filepath):
    with open(filepath) as f:
        for line in f:
            yield line.strip()

def skip_empty(lines):
    for line in lines:
        if line:
            yield line

def parse_entries(lines):
    for line in lines:
        entry = parse_log_entry(line)
        if entry:
            yield entry

def only_errors(entries):
    for entry in entries:
        if entry["level"] in ("ERROR", "WARNING"):
            yield entry

def format_for_report(entries):
    for entry in entries:
        yield (f"{entry['date']} {entry['time']} "
               f"[{entry['level']}] {entry['source']}: {entry['message']}")


# Pipeline - each generator feeds the next
# Nothing runs until you iterate the final generator
pipeline = format_for_report(
    only_errors(
        parse_entries(
            skip_empty(
                read_lines("test_run.log")
            )
        )
    )
)

print("Errors and warnings (pipeline output):")
for formatted_line in pipeline:
    print(f"  {formatted_line}")

# Cleanup
os.remove("test_run.log")