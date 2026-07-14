# DAY 1 - FILE 5: Challenge
# Write all 5 functions yourself. Run with: python3 day1_challenge.py

# CHALLENGE 1
# Write a function that takes a status code
# and returns "pass" if 200-299, "client_error" if 400-499,
# "server_error" if 500+, "unknown" otherwise
def classify_response(status_code):
    # replace with your code
    if 200 <= status_code < 300:
        return "pass"
    elif 400 <= status_code <= 499:
        return "client_error"
    elif status_code >= 500:
        return "server_error"
    else:
        return "unknown"
        

# CHALLENGE 2
# Write a function that takes a base_url and user_id
# and returns the full URL like: https://api.example.com/users/42
# Use an f-string
def build_user_url(base_url, user_id):
    return f"{base_url}/users/{user_id}"
        

# CHALLENGE 3
# Write a function that takes a list of test durations (floats)
# and returns the average rounded to 2 decimal places
def average_duration(durations):
    res = 0
    for i in durations:
        res= res + i
    avg = res / len(durations)
    return float(f"{avg:.2f}")



# CHALLENGE 4
# Write a function that takes a list of test results (dicts with "name" and "status")
# and returns a dict with keys "passed" and "failed" containing lists of test names
# Example input: [{"name": "login", "status": "PASS"}, {"name": "checkout", "status": "FAIL"}]
# Example output: {"passed": ["login"], "failed": ["checkout"]}
def group_results(test_results):
    result = {"passed": [], "failed": []}
    for test in test_results:
        if test["status"] == "PASS":
            result["passed"].append(test["name"])
        else:
            result["failed"].append(test["name"])
    return result


# CHALLENGE 5
# Write a function that takes an email string
# and returns True if it contains "@" and has at least one "." after the "@"
# Do not use any library - just string methods
def is_valid_email(email):
    if "@" not in email:
        return False
    parts = email.split("@")
    # parts[0] = "divya", parts[1] = "test.com"
    domain = parts[1]
    return "." in domain
    
# =============================================
# DO NOT MODIFY BELOW THIS LINE
# These tests will tell you if your code is correct
# =============================================

print("=== TESTING YOUR FUNCTIONS ===\n")

# Test 1
assert classify_response(200) == "pass", "Test 1a failed"
assert classify_response(201) == "pass", "Test 1b failed"
assert classify_response(404) == "client_error", "Test 1c failed"
assert classify_response(500) == "server_error", "Test 1d failed"
assert classify_response(301) == "unknown", "Test 1e failed"
print("CHALLENGE 1: PASSED")

# Test 2
assert build_user_url("https://api.example.com", 42) == "https://api.example.com/users/42", "Test 2 failed"
assert build_user_url("https://staging.api.com", 1) == "https://staging.api.com/users/1", "Test 2b failed"
print("CHALLENGE 2: PASSED")

# Test 3
assert average_duration([1.0, 2.0, 3.0]) == 2.0, "Test 3a failed"
assert average_duration([1.5, 2.5]) == 2.0, "Test 3b failed"
assert average_duration([1.234, 2.346]) == 1.79, "Test 3c failed"
print("CHALLENGE 3: PASSED")

# Test 4
results = [
    {"name": "login", "status": "PASS"},
    {"name": "checkout", "status": "FAIL"},
    {"name": "search", "status": "PASS"},
    {"name": "logout", "status": "FAIL"},
]
grouped = group_results(results)
assert grouped["passed"] == ["login", "search"], "Test 4a failed"
assert grouped["failed"] == ["checkout", "logout"], "Test 4b failed"
print("CHALLENGE 4: PASSED")

# Test 5
assert is_valid_email("divya@test.com") == True, "Test 5a failed"
assert is_valid_email("divya@test") == False, "Test 5b failed"
assert is_valid_email("divyatest.com") == False, "Test 5c failed"
assert is_valid_email("") == False, "Test 5d failed"
print("CHALLENGE 5: PASSED")

print("\nALL CHALLENGES PASSED. Day 1 complete.")

#REPORT -> WASNT ABLE TO SOLVE Q 4 AND 5 (EFFICENT SOLUTION)