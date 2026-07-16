# DAY 2 - FILE 5: Challenge
# Write ALL functions yourself from memory
# Run with: python3 day2_challenge.py

# CHALLENGE 1
# Given a list of API response dicts, each with an "id" field,
# return a set of IDs that appear more than once.
# Input:  [{"id": 1}, {"id": 2}, {"id": 1}, {"id": 3}, {"id": 2}]
# Output: {1, 2}
def find_duplicate_ids(items):
    seen = set()
    duplicate = set()
    for item in items:
        temp_id = item["id"]
        if temp_id in seen:
            duplicate.add(temp_id)
        seen.add(temp_id)
    return duplicate
        

# CHALLENGE 2   -> Solve again
# Given a list of test result dicts (each has "name", "status", "duration"),
# return a new dict with:
#   "total": total number of tests
#   "passed": count of PASS
#   "failed": count of FAIL
#   "pass_rate": percentage passed, rounded to 1 decimal place
#   "slowest": name of the test with highest duration
def summarise_results(results):
    my_dict = {}
    
    passed = [count for count in results if count["status"]== "PASS"]
    passed_count = len(passed)
    
    failed = [count for count in results if count["status"]== "FAIL"]
    failed_count = len(failed)
    
    total = passed_count + failed_count
    
    pass_rate = (passed_count / total)*100
    
    slowest = max(results, key=lambda result: result["duration"])["name"]
    
    my_dict.update({"total": total, "passed": passed_count, "failed": failed_count, "pass_rate": pass_rate, "slowest": slowest})
    
    return my_dict


# CHALLENGE 3
# Given two lists of field names,
# return a dict with three keys:
#   "missing": fields in required but not in actual
#   "extra":   fields in actual but not in required
#   "valid":   True if missing is empty, False otherwise
def validate_response_fields(required, actual):
    my_dict = {}
    required = set(required)
    actual = set(actual)
    missing = required - actual
    extra = actual - required
    
    my_dict.update({"missing": missing, "extra": extra, "valid": not bool(missing)})    
    return my_dict


# CHALLENGE 4
# Given a list of test result dicts (each has "browser" and "status"),
# return a dict where keys are browser names and values are
# dicts with "passed" and "failed" counts.
# Input:  [{"browser": "chromium", "status": "PASS"},
#           {"browser": "firefox", "status": "FAIL"},
#           {"browser": "chromium", "status": "FAIL"}]
# Output: {"chromium": {"passed": 1, "failed": 1},
#           "firefox":  {"passed": 0, "failed": 1}}
def results_by_browser(test_results):
    result = {}
    
    for test in test_results:
        browser = test["browser"]
        status = test["status"] 
        
        # Initialize browser if not present
        if browser not in result:
            result[browser] = {
                "passed" : 0,
                "failed" : 0
            }
        
        #update counts
        if status == "PASS":
            result[browser]["passed"] = result[browser]["passed"] + 1
        else:
            result[browser]["failed"] = result[browser]["failed"] + 1
        
    return result
    

# CHALLENGE 5
# Given a list of strings (test tags),
# return a tuple of (unique_tags, duplicate_tags)
# where unique_tags is a sorted list of tags with no duplicates
# and duplicate_tags is a sorted list of tags that appeared more than once
# Input:  ["smoke", "auth", "smoke", "regression", "auth", "smoke"]
# Output: (["auth", "regression", "smoke"], ["auth", "smoke"])
def analyse_tags(tags):
    unique_tags = []
    duplicate_tags = []

    for tag in tags:
        if tag not in unique_tags:
            unique_tags.append(tag)
        elif tag not in duplicate_tags:
            duplicate_tags.append(tag)

    unique_tags.sort()
    duplicate_tags.sort()

    return (unique_tags, duplicate_tags)


# =============================================
# DO NOT MODIFY BELOW THIS LINE
# =============================================

print("=== TESTING YOUR FUNCTIONS ===\n")

# Test 1
items = [{"id": 1}, {"id": 2}, {"id": 1}, {"id": 3}, {"id": 2}]
assert find_duplicate_ids(items) == {1, 2}, "Challenge 1 failed"
assert find_duplicate_ids([{"id": 1}, {"id": 2}]) == set(), "Challenge 1b failed"
print("CHALLENGE 1: PASSED")

# Test 2
results = [
    {"name": "login", "status": "PASS", "duration": 1.2},
    {"name": "checkout", "status": "FAIL", "duration": 3.8},
    {"name": "search", "status": "PASS", "duration": 0.9},
    {"name": "logout", "status": "PASS", "duration": 0.5},
]
summary = summarise_results(results)
assert summary["total"] == 4, "Challenge 2a failed"
assert summary["passed"] == 3, "Challenge 2b failed"
assert summary["failed"] == 1, "Challenge 2c failed"
assert summary["pass_rate"] == 75.0, "Challenge 2d failed"
assert summary["slowest"] == "checkout", "Challenge 2e failed"
print("CHALLENGE 2: PASSED")

# Test 3
required = ["id", "email", "status", "created_at"]
actual = ["id", "email", "status", "created_at", "avatar"]
check = validate_response_fields(required, actual)
assert check["missing"] == set(), "Challenge 3a failed"
assert check["extra"] == {"avatar"}, "Challenge 3b failed"
assert check["valid"] == True, "Challenge 3c failed"

actual_missing = ["id", "email"]
check2 = validate_response_fields(required, actual_missing)
assert check2["missing"] == {"status", "created_at"}, "Challenge 3d failed"
assert check2["valid"] == False, "Challenge 3e failed"
print("CHALLENGE 3: PASSED")

# Test 4
test_results = [
    {"browser": "chromium", "status": "PASS"},
    {"browser": "firefox", "status": "FAIL"},
    {"browser": "chromium", "status": "FAIL"},
    {"browser": "chromium", "status": "PASS"},
    {"browser": "firefox", "status": "PASS"},
]
by_browser = results_by_browser(test_results)
assert by_browser["chromium"]["passed"] == 2, "Challenge 4a failed"
assert by_browser["chromium"]["failed"] == 1, "Challenge 4b failed"
assert by_browser["firefox"]["passed"] == 1, "Challenge 4c failed"
assert by_browser["firefox"]["failed"] == 1, "Challenge 4d failed"
print("CHALLENGE 4: PASSED")

# Test 5
tags = ["smoke", "auth", "smoke", "regression", "auth", "smoke"]
unique, dupes = analyse_tags(tags)
assert unique == ["auth", "regression", "smoke"], "Challenge 5a failed"
assert dupes == ["auth", "smoke"], "Challenge 5b failed"
print("CHALLENGE 5: PASSED")

print("\nALL CHALLENGES PASSED. Day 2 complete.")