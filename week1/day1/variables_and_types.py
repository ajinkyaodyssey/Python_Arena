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