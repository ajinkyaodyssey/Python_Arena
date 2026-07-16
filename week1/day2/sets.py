# DAY 2 - FILE 4: Sets
# Run with: python3 sets.py

# =============================================
# SECTION 1: Creating and Basic Operations
# =============================================

print("=== CREATING AND BASIC OPERATIONS ===")

#Sets are unordered, no duplicates and o(1) membership check
browsers = {"chromium","firefox","webkit"}
print(browsers)     # order not guaranteed

# Add and remove
browsers.add("edge")
print(browsers)

browsers.discard("edge")            # no error if not present
browsers.discard("safari")          # no error - safe
print(browsers)

browsers.remove("safari")       # KeyError if not present
print(browsers)

#Membership check: O(1) regardless of set size
print("chromium" in browsers)       # True
print("firefox" in browsers)        # False

# Convert list to set - instant deduplication
raw_tags = ["smoke", "auth", "smoke", "regression", "auth", "smoke"]
unique_tags = set(raw_tags)
print(f"Unique tags: {unique_tags}")
print(f"Original count: {len(raw_tags)}, Unique count: {len(unique_tags)}")


# =============================================
# SECTION 2: Set Operations
# =============================================


print("\n=== SET OPERATIONS ===")

required_permissions = {"read", "write", "delete", "admin"}
user_permissions = {"read", "write", "export"}

# Intersection - what they have in common
common = required_permissions & user_permissions
print(common)       #{'write', 'read'}

#Union - everything from both
all_perms = required_permissions | user_permissions
print(all_perms)        #{'write', 'export', 'delete', 'admin', 'read'}

# Difference - in first but NOT in second
missing = required_permissions - user_permissions
print(missing)      #{'delete', 'admin'}

#Symmetric difference - in one but not both
unique_to_each = required_permissions ^ user_permissions
print(unique_to_each)       #{'export', 'delete', 'admin'}

# Subset and superset checks    
basic_perms = {"read", "write"}     
print(f"basic_perms is subset of user_permissions: {basic_perms <= user_permissions}")         #basic_perms is subset of user_permissions: True
print(f"user_permissions is superset of basic_perms: {user_permissions >= basic_perms}")      #user_permissions is superset of basic_perms: True


# =============================================
# SECTION 3: Why Sets Beat Lists for Lookup
# =============================================


print("\n=== SETS VS LISTS FOR LOOKUP ===")

import time

#Create a large  collection
large_list = list(range(10000))
large_set = set(range(10000))
target = 9999

#List lookup - O(n) - scans from beginning
start = time.perf_counter()
found = target in large_list
list_time = time.perf_counter() - start

#Set lookup - O(n) - hash lookup
start = time.perf_counter()
found = target in large_set
set_time = time.perf_counter()-start

print(f"List lookup: {list_time:.6f}s")
print(f"Set lookup:  {set_time:.6f}s")
print(f"Set is ~{list_time/set_time:.0f}x faster for this lookup")
# List lookup: 0.000168s
# Set lookup:  0.000001s
# Set is ~227x faster for this lookup


# =============================================
# SECTION 4: Real Test Automation Patterns
# =============================================


print("\n=== REAL PATTERNS ===")

# Pattern 1: Check all required fields exist in API response
required_fields = {"id", "email", "status", "created_at"}
api_response_fields = {"id", "email", "status", "created_at", "updated_at", "avatar"}

missing_fields = required_fields - api_response_fields
extra_fields = api_response_fields - required_fields

print(f"Missing required fields: {missing_fields}")     # empty set = all present
print(f"Extra fields in response: {extra_fields}")      #Extra fields in response: {'avatar', 'updated_at'}

if not missing_fields:
    print("All required fields present - PASS")
else:
    print(f"Missing fields: {missing_fields}")
    
# Pattern 2: Detect duplicate IDs in a paginated API response
def find_duplicate_ids(items):
    seen = set()
    duplicates = set()
    for item in items:
        item_id = item["id"]
        if item_id in seen:
            duplicates.add(item_id)
        seen.add(item_id)
    return duplicates
    
# Test it
users = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 1, "name": "Alice Duplicate"},  # duplicate!
    {"id": 3, "name": "Charlie"},
    {"id": 2, "name": "Bob Clone"},         # duplicate!
]
dupes = find_duplicate_ids(users)
print(f"\nDuplicate IDs found: {dupes}")        #Duplicate IDs found: {1, 2}
if dupes:
    print(f"DATA INTEGRITY FAIL: Duplicate IDs {dupes}")        #DATA INTEGRITY FAIL: Duplicate IDs {1, 2}
else:
    print("No duplicates - PASS")
    
# Pattern 3: Verify no overlap between test environments
staging_users = {"user_1", "user_2", "test_admin"}
production_users = {"prod_admin", "real_user_1"}

overlap = staging_users & production_users
if overlap:
    print(f"\nDANGER: Test accounts exist in production: {overlap}")
else:
    print("\nSafe: No test accounts in production")