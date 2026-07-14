# DAY 1 - FILE 2: Strings
# Run with: python3 strings.py

BASE_URL = "https://api.example.com"
user_id = 42
endpoint = "/users"

# =============================================
# SECTION 1: String Methods You Will Use Daily
# =============================================

print("=== STRING METHODS ===")

raw = "  standard_user  "
print(raw.strip())              # "standard_user"
print(raw.strip().upper())      # "STANDARD_USER"
print(raw.strip().capitalize()) # "Standard_user"

email = "DIVYA@TEST.COM"
print(email.lower())            # "divya@test.com"

response_text = "Error: Username and password do not match"
print(response_text.startswith("Error"))   # True
print(response_text.endswith("match"))     # True
print("password" in response_text)         # True
print(response_text.replace("Error", "FAIL"))

csv_line = "login,logout,checkout,refund"
print(csv_line.split(","))    #he .split() method splits a string into smaller pieces based on a separator.
test_names = csv_line.split(",")        #['login', 'logout', 'checkout', 'refund']
print(test_names)
print(len(test_names))      #4

rejoined_text = "|".join(test_names)       #The string before .join() is the separator.
print(rejoined_text)        #login|logout|checkout|refund

#NOTE: split() → String ➜ List   AND    join() → List ➜ String

# =============================================
# SECTION 2: f-strings - Use These Always
# =============================================

print("\n=== F-STRINGS ===")

username = "standard_user"
attempt = 3
duration = 1.2567

# Basic f-string
print(f"Testing login for: {username}")     #Testing login for: standard_user

# Expression inside f-string
print(f"Attempt {attempt} of 3")    #Attempt 3 of 3
print(f"Is the last attempt = {attempt == 3}")    #Is the last attempt = True

# Formatting numbers
print(f"Test duration: {duration:.2f}s")    # 1.26s
print(f"Test duration: {duration:.0f}s")    #1s

# Building URLs - you will do this constantly
print(f"{BASE_URL}{endpoint}/{user_id}")     #https://api.example.com/users/42
print(f"{BASE_URL}{endpoint}?page=2&per_page=10")

# Multiline f-string
test_report = (
    f"Test: login_valid\n"
    f"User: {username}\n"
    f"Duration: {duration:.2f}s\n"
    f"STATUS: PASS"
    )
print(test_report)

# =============================================
# SECTION 3: Multiline Strings (for SQL later)
# =============================================

print("\n=== MULTILINE STRINGS ===")

sql_query = """
    SELECT id, email, status
    FROM users
    WHERE status = 'active'
    ORDER BY created_at DESC
"""
print(sql_query)

# =============================================
# SECTION 4: String Checks You Will Use in Tests
# =============================================

print("\n=== STRING CHECKS IN TESTS ===")

error_message = "Username and password do not match"

# These are how you assert in tests
print(error_message.startswith("Username"))   #True
print("do not match" in error_message)      #True
print(error_message == "Username and password do not match")    #True
print(len(error_message)>0)     #True

# Finding index
print(error_message.find("password"))       #13
print(error_message.find("Home"))       #-1 (not found)

# Count occurrences
text = "count,countcount"
print(text.count("count"))      #3
print(text.count("Count"))      #0
#The .count() method counts how many times a substring / character appears inside a string (Case sensitive)