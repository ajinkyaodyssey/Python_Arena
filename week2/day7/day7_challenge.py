# DAY 7 - FILE 3: Challenge
# Write all generators from scratch
# Run with: python3 day7_challenge.py

import os

# =============================================
# CHALLENGE 1: paginated_api_reader
# =============================================
# Write a generator function called paginated_api_reader that:
# - Takes: fetch_func (callable), per_page (int, default=3)
# - fetch_func(page, per_page) returns a dict:
#     {"items": [...], "total_pages": N}
# - Yields each item one at a time across all pages
# - Fetches next page only after current page items are exhausted
# - Stops after the last page

def paginated_api_reader(fetch_func, per_page=3):
    pass  # replace with your implementation


# =============================================
# CHALLENGE 2: log_parser
# =============================================
# Write a generator function called log_parser that:
# - Takes: filepath (str), level (str, default=None)
# - Reads the file one line at a time (never all at once)
# - Each line format: "TIMESTAMP LEVEL MESSAGE"
#   Example: "10:00:01 ERROR Login button not found"
# - If level is None: yields ALL parsed entries as dicts:
#     {"timestamp": "10:00:01", "level": "ERROR", "message": "Login button..."}
# - If level is given: yields ONLY entries matching that level
# - Skips empty lines silently

def log_parser(filepath, level=None):
    pass  # replace with your implementation


# =============================================
# CHALLENGE 3: test_data_generator
# =============================================
# Write a generator function called test_data_generator that:
# - Takes: template (dict), count (int)
# - Yields `count` dicts based on the template
# - For each field in template:
#     if value is a string containing "{n}": replace {n} with current index (1-based)
#     if value is a list: cycle through the list (use index % len(list))
#     otherwise: keep the value as-is
# Example:
#   template = {"email": "user{n}@test.com", "role": ["admin","tester"], "active": True}
#   count = 4
#   Yields:
#     {"email": "user1@test.com", "role": "admin",  "active": True}
#     {"email": "user2@test.com", "role": "tester", "active": True}
#     {"email": "user3@test.com", "role": "admin",  "active": True}
#     {"email": "user4@test.com", "role": "tester", "active": True}

def test_data_generator(template, count):
    pass  # replace with your implementation


# =============================================
# CHALLENGE 4: find_in_stream
# =============================================
# Write a generator function called find_in_stream that:
# - Takes: source_generator (generator), predicate (callable)
# - Yields only items from source_generator where predicate(item) is True
# - Must work with ANY generator as input (generic filter)
# - This is a generator pipeline component

def find_in_stream(source_generator, predicate):
    pass  # replace with your implementation


# =============================================
# DO NOT MODIFY BELOW THIS LINE
# =============================================

print("=== TESTING GENERATORS ===\n")

# --- Test 1: paginated_api_reader basic ---
call_log = []

def make_fetch_func(total_items):
    def fetch(page, per_page):
        call_log.append(page)
        start = (page - 1) * per_page
        end = min(start + per_page, total_items)
        items = [{"id": i + 1} for i in range(start, end)]
        total_pages = (total_items + per_page - 1) // per_page
        return {"items": items, "total_pages": total_pages}
    return fetch

fetch = make_fetch_func(7)
all_items = list(paginated_api_reader(fetch, per_page=3))
assert len(all_items) == 7, f"Test 1a: expected 7 items, got {len(all_items)}"
assert all_items[0]["id"] == 1, "Test 1b: first item should have id=1"
assert all_items[-1]["id"] == 7, "Test 1c: last item should have id=7"
print("TEST 1 PASSED: paginated_api_reader yields all items")

# --- Test 2: paginated_api_reader fetches lazily ---
call_log.clear()
fetch2 = make_fetch_func(9)
gen = paginated_api_reader(fetch2, per_page=3)
first = next(gen)       # should fetch page 1 only
assert 1 in call_log, "Test 2a: page 1 should be fetched"
assert 2 not in call_log, "Test 2b: page 2 should NOT be fetched yet"
assert first["id"] == 1, "Test 2c: first item id should be 1"
print("TEST 2 PASSED: paginated_api_reader fetches lazily")

# --- Test 3: log_parser all levels ---
log_content = """10:00:01 INFO Login page loaded
10:00:02 ERROR Button not found
10:00:03 WARNING Slow response 1500ms
10:00:04 INFO Test passed

10:00:05 ERROR Timeout occurred
"""

with open("test_challenge.log", "w") as f:
    f.write(log_content)

all_entries = list(log_parser("test_challenge.log"))
assert len(all_entries) == 5, f"Test 3a: expected 5 entries, got {len(all_entries)}"
assert all_entries[0]["timestamp"] == "10:00:01", "Test 3b failed"
assert all_entries[0]["level"] == "INFO", "Test 3c failed"
assert all_entries[0]["message"] == "Login page loaded", "Test 3d failed"
print("TEST 3 PASSED: log_parser parses all entries")

# --- Test 4: log_parser filtered by level ---
errors = list(log_parser("test_challenge.log", level="ERROR"))
assert len(errors) == 2, f"Test 4a: expected 2 errors, got {len(errors)}"
assert all(e["level"] == "ERROR" for e in errors), "Test 4b failed"
assert errors[0]["message"] == "Button not found", "Test 4c failed"
assert errors[1]["message"] == "Timeout occurred", "Test 4d failed"
print("TEST 4 PASSED: log_parser filters by level")

# --- Test 5: log_parser is lazy (generator not list) ---
import types
result = log_parser("test_challenge.log")
assert isinstance(result, types.GeneratorType), \
    "Test 5a: log_parser must return a generator, not a list"
print("TEST 5 PASSED: log_parser returns a generator")

os.remove("test_challenge.log")

# --- Test 6: test_data_generator basic ---
template = {
    "email": "user{n}@test.com",
    "role": ["admin", "tester"],
    "active": True
}
generated = list(test_data_generator(template, count=4))
assert len(generated) == 4, f"Test 6a: expected 4 items, got {len(generated)}"
assert generated[0]["email"] == "user1@test.com", "Test 6b failed"
assert generated[1]["email"] == "user2@test.com", "Test 6c failed"
assert generated[3]["email"] == "user4@test.com", "Test 6d failed"
assert generated[0]["role"] == "admin", "Test 6e failed"
assert generated[1]["role"] == "tester", "Test 6f failed"
assert generated[2]["role"] == "admin", "Test 6g: should cycle back to admin"
assert generated[0]["active"] == True, "Test 6h failed"
print("TEST 6 PASSED: test_data_generator produces correct data")

# --- Test 7: test_data_generator count ---
short = list(test_data_generator({"id": "{n}"}, count=3))
assert len(short) == 3, "Test 7a failed"
assert short[0]["id"] == "1", "Test 7b: {n} should be replaced with 1-based string"
assert short[2]["id"] == "3", "Test 7c failed"
print("TEST 7 PASSED: test_data_generator respects count")

# --- Test 8: find_in_stream basic ---
def number_source():
    for n in [1, 5, 2, 8, 3, 9, 4, 7, 6]:
        yield n

result = list(find_in_stream(number_source(), lambda x: x > 5))
assert result == [8, 9, 7, 6], f"Test 8a: expected [8,9,7,6], got {result}"
print("TEST 8 PASSED: find_in_stream filters correctly")

# --- Test 9: find_in_stream is lazy ---
source = number_source()
filtered = find_in_stream(source, lambda x: x > 5)
assert isinstance(filtered, types.GeneratorType), \
    "Test 9a: find_in_stream must return a generator"
first_match = next(filtered)
assert first_match == 8, f"Test 9b: expected 8, got {first_match}"
print("TEST 9 PASSED: find_in_stream returns a generator")

# --- Test 10: Pipeline - combine generators ---
# Read paginated data -> filter by condition -> collect results
fetch3 = make_fetch_func(10)
all_ids_gen = paginated_api_reader(fetch3, per_page=4)
high_ids = find_in_stream(all_ids_gen, lambda item: item["id"] > 7)
result = list(high_ids)
assert len(result) == 3, f"Test 10a: expected 3 items with id > 7, got {len(result)}"
assert all(item["id"] > 7 for item in result), "Test 10b failed"
print("TEST 10 PASSED: generator pipeline works")

print("\nALL 10 TESTS PASSED. Day 7 complete.")