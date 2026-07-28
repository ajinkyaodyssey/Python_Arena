# DAY 7 - FILE 1: How Generators Actually Work
# Run with: python3 generator_fundamentals.py


# =============================================
# SECTION 1: The problem generators solve
# =============================================


print("=== THE PROBLEM GENERATORS SOLVE ===")

# Regular function - builds entire result in memory BEFORE returning\
def get_all_tests_ids_regular(total):
    result = []
    for i in range (1, total+1):
        result.append(f"TEST-{i:04d}")      ## {i:04d} formats i as a 4-digit integer, padding with leading zeros if needed (e.g., 1 -> 0001).
    return result       # ALL 1 million items in memory at once

# If total = 1_000_000, this holds 1 million strings in memory
# before you see a single one

ids = get_all_tests_ids_regular(5)
print(f"Regular: {ids}")        #Regular: ['TEST-0001', 'TEST-0002', 'TEST-0003', 'TEST-0004', 'TEST-0005']

# Generator function - produces ONE value at a time, on demand
def get_all_test_ids_generator(total):
    for i in range(1, total+1):
        yield f"TEST-{i:04d}"       # pauses here, gives value, resumes on next call
    # when the loop ends, generator raises StopIteration automatically
    
# Nothing is computed yet - generator object created but not run
gen = get_all_test_ids_generator(5)
print(f"\nGenerator object: {gen}")     #Generator object: <generator object get_all_test_ids_generator at 0x7d73f7bd92a0>
print(f"Type: {type(gen)}")             #Type: <class 'generator'>

# Values produced one at a time only when requested
print(f"\nFirst: {next(gen)}")      #First: TEST-0001
print(f"Second: {next(gen)}")   # TEST-0002 - resumes, runs until next yield
print(f"Third:  {next(gen)}")   # TEST-0003

gen2 = get_all_test_ids_generator(5)
for test_id in gen2:
    print(f"  {test_id}")
#   TEST-0001
#   TEST-0002
#   TEST-0003
#   TEST-0004
#   TEST-0005


# =============================================
# SECTION 2: yield vs return — the key difference
# =============================================


print("\n=== YIELD VS RETURN ===")

def return_example():
    print("Before return")
    return "value"
    print("This NEVER runs")        # unreachable
    
def yield_example():
    print(" Before first yield")
    yield "first"
    print(" After first yield, before second")  # DOES run on resume
    yield "second"
    print(" After second yield, before return")
    # function ends here, StopIteration raised
    
print("--- return ---")
result = return_example()
print(f" Got - {result}")   
#Before return
# Got - value

print("--- yield ---")
gen = yield_example()
print(f" Got - {next(gen)}")
# Before first yield
# Got - first
print(f" Got - {next(gen)}")
# After first yield, before second
# Got - second
try:
    next(gen)                   # resumes, function ends, StopIteration raised
except StopIteration:
    print("  StopIteration - generator exhausted")
    

# =============================================
# SECTION 3: Generator state is preserved between yields
# =============================================


def counter_with_state(start, step):
    current = start
    count = 0
    while True:             # infinite generator - runs until caller stops
        yield current       #Returns the current value to the caller, Pauses the function here, The values of current and count are saved.
        current += step     #When next() is called again, execution resumes here.
        count += 1
        if count % 3 == 0:
            print(f"  [internal state] Generated {count} values so far")
            
gen = counter_with_state(0, 10)
for _ in range(9):      #_ means "I don't care about this variable". It's just a convention for an unused loop variable
    value = next(gen)
    print(f"  value: {value}")
#   value: 0
#   value: 10
#   value: 20
#   [internal state] Generated 3 values so far
#   value: 30
#   value: 40
#   value: 50
#   [internal state] Generated 6 values so far
#   value: 60
#   value: 70
#   value: 80


# =============================================
# SECTION 4: Generator expressions
# =============================================


print("\n=== GENERATOR EXPRESSIONS ===")

#List comprehension - computes ALL values immediately
list_comp = [x*x for x in range(1_000_000)]
#1 million integers in memory right now

#Generator comprehension - computes nothing yet
gen_exp = (x*x for x in range(1_000_000))       #notice(), because it creates Generators
# Zero items in memory - just the recipe

print(f"List comp type: {type(list_comp)}")     #List comp type: <class 'list'>
print(f"Gen exp type:   {type(gen_exp)}")       #Gen exp type:   <class 'generator'>

# Use generator expression when you only iterate once
# and don't need random access or len()
squares_sum = sum(x*x for x in range(1000))     # no [] needed inside sum()
print(f"Sum of first 1000 squares: {squares_sum}")      #Sum of first 1000 squares: 332833500
# Note: If you're passing a comprehension directly to a function like sum(), max(), min(), any(), all(), or sorted(), a generator expression ((...)) is often the better choice because the function can consume the values one at a time.

# Filter with generator expression
status_codes = [200, 404, 500, 201, 403, 422, 204]
error_codes = (code for code in status_codes if code>= 400)
print(f"\nError codes:")
for code in error_codes:
    print(f" {code}")
# Error codes:
#  404
#  500
#  403
#  422


# =============================================
# SECTION 5: When to use generator vs list
# =============================================


print("\n=== GENERATOR VS LIST — WHEN TO CHOOSE ===")

import sys

# Measure memory difference
numbers_list = [x for x in range(100_000)]
numbers_gen = (x for x in range(100_000))

print(f"List size in memory: {sys.getsizeof(numbers_list)} bytes")        
print(f"Generator size in memory: {sys.getsizeof(numbers_gen)} bytes")       

# Use LIST when:
# - You need to access items by index (items[5])
# - You need len()
# - You need to iterate multiple times
# - You need to sort or reverse

# Use GENERATOR when:
# - You only iterate once
# - Data is large or infinite
# - You want to start processing before all data is ready
# - You are chaining operations (pipeline)

print("""
Use LIST when:
  - Need index access: items[5]
  - Need len()
  - Iterate more than once
  - Need to sort/reverse

Use GENERATOR when:
  - Only iterate once
  - Large or infinite data
  - Want lazy evaluation
  - Building a pipeline
""")