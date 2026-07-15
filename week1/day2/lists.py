# DAY 2 - FILE 1: Lists
# Run with: python3 lists.py

# =============================================
# SECTION 1: Creating and Accessing
# =============================================

print("=== CREATING AND ACCESSING ===")

test_names = ["login", "logout", "checkout", "search", "refund"]

print(test_names[0])        # login - first item
print(test_names[-1])       # refund - last item
print(test_names[-2])       # search - second to last
print(test_names[1:3])      #['logout', 'checkout'] - index 1 and 2, NOT 3
print(test_names[:2])       # ['login', 'logout'] - first two
print(test_names[2:])       # ['checkout', 'search', 'refund'] - from index 2 onwards
print(test_names[::2])      # ['login', 'checkout', 'refund'] - every other
print(test_names[::-1])     # reversed list


# =============================================
# SECTION 2: Modifying Lists
# =============================================


print("\n=== MODIFYING LISTS ===")

tests = ["login", "logout", "checkout"]

tests.append("refund")              # add to END
print(tests)                        # ['login', 'logout', 'checkout', 'refund']

tests.insert(1, "search")           # insert at index 1, shifts rest right
print(tests)                        # ['login', 'search', 'logout', 'checkout', 'refund']

tests.remove("logout")              # removes FIRST occurrence of this value
print(tests)                        # ['login', 'search', 'checkout', 'refund']

popped = tests.pop()                # removes and returns LAST item
print(f"Popped: {popped}")          # refund
print(tests)                        # ['login', 'search', 'checkout']

popped_at = tests.pop(0)            # removes and returns item at index 0
print(f"Popped at 0: {popped_at}") # login
print(tests)                        # ['search', 'checkout']

tests[0] = "SEARCH_UPDATED"         # update by index
print(tests)                        #['SEARCH_UPDATED', 'checkout']


# =============================================
# SECTION 3: List Methods
# =============================================


print("\n=== LIST METHODS ===")

durations = [3.2, 1.1, 2.8, 0.5, 4.1, 1.1]

print(f"Lenght: {len(durations)}")
print(f"Sum: {sum(durations)}")
print(f"Max: {max(durations)}")
print(f"Max: {min(durations)}")
print(f"Count of 1.1: {durations.count(1.1)}")
print(f"Index of 2.8: {durations.index(2.8)}")
print(f"is 0.5 in list: {0.5 in durations}")
print(f"is 9.9 in list: {9.9 in durations}")

sorted_asc = sorted(durations)      # returns NEW list, original unchanged
print(f"Orignal list: {durations}")
print(f"Sorted list: {sorted_asc}")

durations.sort()
print(f"After .sort(): {durations}")    # sorts IN PLACE, modifies original

durations.sort(reverse = True)
print(f"Sorted desc: {durations}")

# Sort by custom key
tests_with_duration = [
    {"name": "checkout", "duration": 3.2},
    {"name": "login", "duration": 0.8},
    {"name": "search", "duration": 1.5},
    {"name": "logout", "duration": 0.3},
]
by_duration = sorted(tests_with_duration, key=lambda t: t["duration"])
print(f"\nSorted by duration:")
for t in by_duration:
    print(f"  {t['name']}: {t['duration']}s")


# =============================================
# SECTION 4: List Comprehensions
# =============================================


print("\n=== LIST COMPREHENSIONS ===")

status_codes = [200, 404, 500, 201, 403, 422, 204, 429]

# Filter only error codes
#[NEW_VALUE for ITEM in COLLECTION if CONDIITION]

#code (at the beginning) → Add that value to the new list.
#for code in status_codes → Loop through every item in status_codes.
#if code >= 400 → Keep only status codes that are 400 or higher.
errors = [code for code in status_codes if code >= 400]
print(f"Errors: {errors}")

# Transform
labels = [f"HTTPS-{code}" for code in status_codes]
print(f"Labels: {labels}")      #Labels: ['HTTPS-200', 'HTTPS-404', 'HTTPS-500', 'HTTPS-201', 'HTTPS-403', 'HTTPS-422', 'HTTPS-204', 'HTTPS-429']

# Filter AND transform together
error_labels = [f"HTTPS-{code}" for code in status_codes if code >= 400]
print(f"Error labels: {error_labels}")      #Error labels: ['HTTPS-404', 'HTTPS-500', 'HTTPS-403', 'HTTPS-422', 'HTTPS-429']

# Nested - flatten a list of lists
all_tags = [["smoke", "auth"], ["regression"], ["smoke", "payments", "critical"]]
flat_tags = [tag for sublist in all_tags for tag in sublist]
print(f"Flat tags: {flat_tags}")


# =============================================
# SECTION 5: Common List Patterns in Test Code
# =============================================


print("\n=== PATTERNS IN TEST CODE ===")

api_responses = [
    {"id": 1, "status": "active"},
    {"id": 2, "status": "inactive"},
    {"id": 3, "status": "active"},
    {"id": 4, "status": "active"},
]

# Extract all IDs
all_ids = [r["id"] for r in api_responses]    # From the current dictionary r, give me the value stored under the key "id"
print(all_ids)      #[1, 2, 3, 4]

# Filter active users
active = [r for r in api_responses if r["status"] == "active"]      #For each response r, if its status is 'active', add the entire dictionary r to the new list.
print(active)

#check all are active
#all() function is a built-in function that checks whether every item in an iterable is True.
all_active = all(r["status"] == "active" for r in api_responses)    #The key idea is that all() expects a series of True or False values, not the dictionaries themselves
print(all_active)

# Check any are inactive
#any() -> True if at least one item in an iterable is truthy, False if all items are falsy
any_inactive = any(r["status"] == "inactive" for r in api_responses)
print(any_inactive)