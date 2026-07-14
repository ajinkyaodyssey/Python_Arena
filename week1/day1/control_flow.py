# DAY 1 - FILE 3: Control Flow
# Run with: python3 control_flow.py


# =============================================
# SECTION 1: if / elif / else
# =============================================


print("=== IF/ELIF/ELSE ===")

def classify_status_code(code):
    if code == 200:
        return "OK - SUCCESS"
    elif code == 201:
        return "Created - Resource created"
    elif code == 204:
        return "No Content - Deleated successfully"
    elif 400 <= code < 500:
        return f"Client Error - Code: {code}"
    elif code >= 500:
        return f"Server error - Code: {code}"
    else:
        return f"Unknown code: {code}"
    
print(classify_status_code(300))    #Unknown code: 300
print(classify_status_code(450))    #Client Error - Code: 450
print(classify_status_code(200))    #OK - SUCCESS
print(classify_status_code(201))    #Created - Resource created
print(classify_status_code(404))    #Client Error - Code: 404
print(classify_status_code(500))    #Server error - Code: 500
print(classify_status_code(422))    #Client Error - Code: 422

# Ternary - one liner conditional
status = 200
result = "PASS" if status == 200 else "FAIL"
print(result)


# =============================================
# SECTION 2: for loops
# ===========================================


print("\n=== FOR LOOPS ===")

endpoints = ["/users", "/orders", "/products", "/auth"]

# Basic for
for endpoint in endpoints:
    print(f"Testing endpoint : {endpoint}")
    
# enumerate - when you need index AND value
print("\n--- with enumerate ---")     #returns (index, item)
for index, endpoint in enumerate(endpoints, start = 1):   #enumerate(endpoints, 1)
    print(f"{index}.{endpoint}")

# range
print("\n--- range examples ---")

for i in range(5):
    print(i)        #  0 1 2 3 4
    
for i in range(1,6):
    print(i)        #1 2 3 4 5
    
for i in range(0,10,2):
    print(i)        #0 2 4 6 8
    
# Looping over a dict
print("\n--- looping over dict ---")
test_data = {
    "username": "standard_user",
    "password": "secret_sauce",
    "expected_url": "/inventory.html"
}
for key, value in test_data.items():
    print(f"{key}: {value}")
    
    
# =============================================
# SECTION 3: while loops
# =============================================


print("\n=== WHILE LOOPS ===")

def simulate_api_call(attempt_number):
    return attempt_number >= 3

max_retries = 3
attempt = 1
success = False

while attempt <= max_retries:
    print(f"Attempt: {attempt}")
    if simulate_api_call(attempt):
        success = True
        print(f"Success on attempt : {attempt}")
        break
    print("Failed... retrying")
    attempt+=1
    
if not success:
    print("All retries exhausted")


# =============================================
# SECTION 4: break and continue
# =============================================


print("\n=== BREAK AND CONTINUE ===")

test_names = ["login", "skip_this", "checkout", "STOP_HERE", "refund"]
for test in test_names:
    if test == "skip_this":
        print(f"  Skipping: {test}")
        continue        # goes to next iteration
    if test == "STOP_HERE":
        print(f"  Stopping at: {test}")
        break       #exits the loop entirely
    print(f"  Running: {test}")

# Output: Running login, Skipping skip_this, Running checkout, Stopping at STOP_HERE
# refund never runs

# =============================================
# SECTION 5: range() in depth
# =============================================

print("\n=== RANGE IN DEPTH ===")

#range(stop)
print(list(range(5)))       #[0, 1, 2, 3, 4]

# range(start, stop)
print(list(range(1,6)))     #[1, 2, 3, 4, 5]

# range(start, stop, step)  
print(list(range(0,10,2)))      #[0, 2, 4, 6, 8]

# Countdown
print(list(range(10,-1, -2)))       #[10, 8, 6, 4, 2, 0]

# Real use case: paginated API calls
total_pages = 5
for page in range(1, total_pages+1):
    print(f"Fetching page {page} of {total_pages}")