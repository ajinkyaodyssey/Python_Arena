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
