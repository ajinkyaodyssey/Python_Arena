# DAY 2 - FILE 3: Dictionaries
# Run with: python3 dicts.py


# =============================================
# SECTION 1: Creating and Accessing
# =============================================


print("=== CREATING AND ACCESSING ===")

user = {
    "id": 101,
    "email": "divya@test.com",
    "role": "sdet",
    "is_active": True,
    "score": 98.5
}

#Access - two ways   (simple way to get value is use [])
print(user["email"])                        # direct - KeyError if missing
print(user.get("email"))                    # safe - None if missing
print(user.get("phone"))                    # None - no error
print(user.get("phone", "NOT SET"))         # "NOT SET" - custom default
print(user.get("id", 0))                    # 101 - key exists so returns value

# KeyError demo
try:
    print(user["phone"])
except KeyError as e:
    print(f"KeyError: {e}")
    

# =============================================
# SECTION 2: Modifying
# =============================================


print("\n=== MODIFYING ===")
user["role"] = "senior_sdet"        # update existing key
user["team"] = "platform"       # add new key
user["joining_date"] = "2023-01-15"
print(user)

del user["joining_date"]        #deleting a key
print(f"After delete: {'joining_date' in user}")        # False

popped = user.pop("team", "not-found")      # remove and return, with default
print(f"Popped Team: {popped}")

# Update multiple keys at once
user.update({"role": "lead_sdet", "level": 3, "manager": "Arjun"})      #dont forget to add {}
print(user)


# =============================================
# SECTION 3: Iteration
# =============================================


print("\n=== ITERATION ===")

config = {
    "base_url": "https://staging.example.com",
    "api_url": "https://api-staging.example.com",
    "timeout": 30,
    "headless": True,
    "browser": "chromium"
}

# Keys only
for key in config:
    print(f"Keys: {key}")

#values only
for value in config.values():
    print(f"Values: {value}")
    
# Both - use this most often
for key, value in config.items():
    print(f"Key: {key}, Value: {value}")
    
# Check membership - checks KEYS by default
print(f"\n'timeout' in config: {"timeout" in config}")      #True
print(f"'firefox' in config: {'firefox' in config}")        #False
print(f"'firefox' in config.values(): {'firefox' in config.values()}")      #False


# =============================================
# SECTION 4: Nested Dicts - API Responses
# =============================================


print("\n=== NESTED DICTS ===")

# This is what real API responses look like
api_response = {
    "status": "success",
    "data": {
        "user": {
            "id": 42,
            "email": "divya@test.com",
            "profile": {
                "first_name": "Divya",
                "last_name": "Kumar",
                "avatar_url": "https://cdn.example.com/avatars/42.jpg"
            }
        },
        "permissions": ["read", "write", "delete"],
        "metadata": {
            "last_login": "2024-01-15T10:30:00Z",
            "login_count": 47
        }
    },
    "pagination": {
        "page": 1,
        "per_page": 10,
        "total": 150
    }
}

# Accessing nested values
user_id = api_response["data"]["user"]["id"]
print(user_id)      #42
user_first_name = api_response["data"]["user"]["profile"]["first_name"]
print(user_first_name)      #Divya
user_permissions = api_response["data"]["permissions"]
print(user_permissions)     #['read', 'write', 'delete']
total_records = api_response["pagination"]["total"]
print(total_records)    #150

print(f"User ID: {user_id}")
print(f"First Name: {user_first_name}")
print(f"Permissions: {user_permissions}")
print(f"Total Records: {total_records}")
print(f"Has delete permission: {'delete' in user_permissions}")

# Safe nested access - when any level might be missing
user_phone = api_response.get("data", {}).get("user", {}).get("phone",{})
print(user_phone)       #{}


# =============================================
# SECTION 5: Dict Comprehensions
# =============================================


print("\n=== DICT COMPREHENSIONS ===")

status_codes = [200, 201, 204, 400, 401, 403, 404, 500]

# Create a lookup dict
code_type = {
    code: "success" if code < 400 else "error"
    for code in status_codes
}
print(code_type)

# Invert a dict (swap keys and values)
original = {"login": "PASS", "checkout": "FAIL", "search": "PASS"}
inverted = {value: key for key, value in original.items()}
print(inverted)     # Note: duplicate values will overwrite

# Filter a dict
only_passing = {name: status for name, status in original.items() if status == "PASS"}
print(only_passing)


# =============================================
# SECTION 6: defaultdict - Grouping Pattern
# =============================================


print("\n=== DEFAULTDICT ===")

from collections import defaultdict

test_results = [
    {"name": "login", "browser": "chromium", "status": "PASS"},
    {"name": "login", "browser": "firefox", "status": "FAIL"},
    {"name": "checkout", "browser": "chromium", "status": "PASS"},
    {"name": "search", "browser": "chromium", "status": "PASS"},
    {"name": "checkout", "browser": "firefox", "status": "PASS"},
]

# Group by browser - without defaultdict you'd need to check if key exists first
by_browser = defaultdict(list)
for result in test_results:
    by_browser[result["browser"]].append(result["name"])

for browser, tests in by_browser.items():
    print(f"  {browser}: {tests}")