# DAY 1 - FILE 1: Variables and Data Types
# Run this file with: python3 variables_and_types.py

# =============================================
# SECTION 1: Core Data Types
# =============================================

name = "John"  # String
age = 30    #int
experience = 5.5    #float
is_automation_capable = False
pending_tasks = None

print("===Core Types===")
print(name)         #John
print(type(name))       # <class 'str'>
print(type(age))        # <class 'int'>
print(type(experience))         # <class 'float'>
print(type(is_automation_capable))      # <class 'bool'>
print(type(pending_tasks))      # <class 'NoneType'>

# =============================================
# SECTION 2: Type Checking
# =============================================

print("\n===Type Checking===")
print(isinstance(name,str))       #True
print(isinstance(age,int))        #True
print(isinstance(experience, int))      #False

# =============================================
# SECTION 3: Type Conversion
# =============================================

print("\n=== TYPE CONVERSION ===")
raw_id = "42"
user_id = int(raw_id)
print(user_id)      #42
print(type(user_id))        #<class 'int'>

print("\n")
price = 499.99
price_as_str = str(price)
print(price_as_str)
print(type(price_as_str))

flag_zero = bool(0)
flag_one = bool(1)
flag_from_string = bool("")
flag_from_text = bool("hello")
print(flag_zero)
print(flag_one)
print(flag_from_string)
print(flag_from_text)

# =============================================
# SECTION 4: Falsy Values - MEMORISE THESE
# =============================================

print("\n=== FALSY VALUES ===")
falsy_examples = [False, 0, 0.0, "", [], {}, (), set(), None]
for value in falsy_examples:   #"Go through every item in the list (or other iterable) called falsy_examples, one at a time, and store the current item in the variable value."
    print(f"bool({repr(value)}) = {bool(value)}")
    

# =============================================
# SECTION 5: Why This Matters in Test Code
# =============================================

print("\n=== WHY THIS MATTERS IN TESTS ===")

# Scenario: API returns empty response body
api_response = {}
if not api_response:
    print("PROBLEM: Empty response body - test should fail here")

# Scenario: user_id comes back as 0 - falsy but valid
user_id_from_api = 0
if not user_id_from_api:
    print("BUG: This fires even though 0 might be a valid ID")
    print("Always use: if user_id_from_api is None")
    
# Correct way
if user_id_from_api is None:
    print("This correctly checks for missing value only")
else:
    print(f"Got user_id: {user_id_from_api}")  # this prints correctly