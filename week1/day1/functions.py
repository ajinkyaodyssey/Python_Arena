# DAY 1 - FILE 4: Functions
# Run with: python3 functions.py

# =============================================
# SECTION 1: Basic Functions
# =============================================

print("=== BASIC FUNCTIONS ===")

def check_status_code(actual, expected = 200):
    print("Check if the actual status code matches")
    if actual == expected:
        return True
    else:
        return False
    
print(check_status_code(200))           # True - uses default expected=200
print(check_status_code(404))           # False
print(check_status_code(201, 201))      # True - positional
print(check_status_code(201, expected=201))  # True - keyword


# =============================================
# SECTION 2: Default Arguments
# =============================================


print("\n=== DEFAULT ARGUMENTS ===")

def build_url(base, endpoint, version ="v1", secure = True):
    protocol = "https" if secure else "http"
    return f"{protocol}://{base}/api/{version}{endpoint}"

print(build_url("example.com", "/users"))
print(build_url("example.com", "/users", version="v2"))
print(build_url("example.com", "/users", secure=False))
print(build_url("example.com", "/users", "v2", False))


# =============================================
# SECTION 3: *args
# =============================================


print("\n=== *ARGS ===")   #The * collects all extra positional arguments into a tuple.

def log_test_result(test_name, status, *tags):
    print(f"Test: {test_name}")
    print(f"State: {status}")
    print(f"Tags: {tags}")      #tuple
    print(f"Tag count: {len(tags)}")
    
log_test_result("login_valid", "PASS")
print("---")
log_test_result("login_valid", "PASS", "smoke", "auth")
print("---")
log_test_result("checkout_flow", "FAIL", "regression", "payments", "critical", "p0")


# =============================================
# SECTION 4: **kwargs
# =============================================


print("\n=== **KWARGS ===")     #**kwargs, which collects keyword arguments into a DICTIONARY

def create_test_report(test_name, **details):
    print(f"\nReport for: {test_name}")
    for key, value in details.items():      #details.items() returns each key-value pair from the dictionary.
        print(f" {key}: {value}")
        
create_test_report("login_test", 
    duration = 1.23,
    passed = True,
    retries = 0,
    browser = "chromium",
    environment = "staging")
    

# =============================================
# SECTION 5: Return multiple values
# =============================================

print("\n=== MULTIPLE RETURN VALUES ===")

def run_test(test_name):
    # Simulated test run
    passed = True
    duration = 1.45
    error = None
    return passed, duration, error          # returns a tuple

result, time, err = run_test("login_test")
print(f"Passed: {result}")
print(f"Duration: {time}s")
print(f"Error: {err}")


# =============================================
# SECTION 6: Lambda
# =============================================


print("\n=== LAMBDA ===")

double = lambda x: x * 2
print(double(5))    # 10

tests = [
    {"name": "checkout", "duration": 3.2},
    {"name": "login", "duration": 0.8},
    {"name": "search", "duration": 1.5},
]

# Sort by duration - shortest first
sorted_tests = sorted(tests, key=lambda t: t["duration"])
for t in sorted_tests:
    print(f"  {t['name']}: {t['duration']}s")

# Filter only slow tests (> 2s)
slow_tests = list(filter(lambda t: t["duration"] > 2, tests))
print(f"\nSlow tests: {[t['name'] for t in slow_tests]}")