# DAY 2 - FILE 2: Tuples
# Run with: python3 tuples.py

# =============================================
# SECTION 1: Tuples vs Lists
# =============================================

print("=== TUPLES VS LISTS ===")

# Tuple - immutable (cannot change after creation)
test_config = ("staging", "chromium", 1280, 720)
print(test_config)
print(test_config[0])       # staging
print(test_config[-1])      # 720
print(len(test_config))     # 4

# Try to modify - this will raise TypeError
try:
    test_config[0] = "production"
except TypeError as e:
    print(f"Cannot modify Tuples: {e}")
    
# List - mutable (can change)
test_list = ["staging", "chromium", 1280, 720]
test_list[0] = "production"     # this works fine
print(test_list)


# =============================================
# SECTION 2: Tuple Unpacking
# =============================================


print("\n=== TUPLE UNPACKING ===")

# Basic unpacking
browser, width, height = ("chromium", 1280, 720)
print(f"Browser: {browser}, Width: {width}, Height: {height}")      #Browser: chromium, Width: 1280, Height: 720

# Swap variables using tuple unpacking
a = "first"
b = "second"
a, b = b, a         # Python swaps using tuple under the hood
print(f"a={a}, b={b}")

# Extended unpacking with *
first, *middle, last = (1,2,3,4,5)
print(f"first={first}, middle={middle}, last={last}")       #first=1, middle=[2, 3, 4], last=5

# Unpacking in loops
test_cases = [
    ("login_valid", "standard_user", "secret_sauce", True),
    ("login_invalid", "wrong_user", "wrong_pass", False),
    ("login_locked", "locked_out_user", "secret_sauce", False),
]
for test, username, password, should_pass in test_cases:
    print(f"Test case: {test}, Username: {username}, Password: {password}, Status: {should_pass}")


# =============================================
# SECTION 3: Tuples as Dict Keys
# =============================================


print("\n=== TUPLES AS DICT KEYS ===")

# Tuples are hashable so they can be dict keys
# Lists cannot be dict keys (unhashable)

test_results = {
    ("login", "chromium", "staging"): "PASS",
    ("login", "firefox", "staging"): "FAIL",
    ("checkout", "chromium", "staging"): "PASS",
    ("checkout", "chromium", "production"): "PASS",
}

# Lookup result for a specific combination
key = ("login", "firefox", "staging")
print(f"Result for {key} is: {test_results[key]}")

# Try with list as key - fails
try:
    bad_dict = {["login", "chromium"]: "PASS"}
except TypeError as e:
    print(f"List cannot be dict key: {e}")
    

# =============================================
# SECTION 4: Named Tuples
# =============================================


print("\n=== NAMED TUPLES ===")

from collections import namedtuple

# Define a named tuple type
TestResult = namedtuple("TestResult", ["name", "status", "duration", "browser"])

# Create instances
r1 = TestResult("login_test", "PASS", 1.23, "chromium")
r2 = TestResult("checkout_test", "FAIL", 3.45, "firefox")

# Access by name (readable) instead of index (confusing)
print(f"{r1.name}: {r1.status} in {r1.duration}s on {r1.browser}")
print(f"{r2.name}: {r2.status} in {r2.duration}s on {r2.browser}")

# Still works like a regular tuple
print(r1[0])        # login_test
name, status, duration, browser = r1    # unpacking still works

# Group results
results = [r1, r2,
           TestResult("search_test", "PASS", 0.8, "chromium"),
           TestResult("login_test", "PASS", 1.1, "firefox")]

passed = [r for r in results if r.status == "PASS"]
print(f"\nPassed tests: {[r.name for r in passed]}")
print(f"Average duration: {sum(r.duration for r in results) / len(results):.2f}s")