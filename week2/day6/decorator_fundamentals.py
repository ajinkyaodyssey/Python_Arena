# DAY 6 - FILE 1: How Decorators Actually Work
# Run with: python3 decorator_fundamentals.py


# =============================================
# SECTION 1: Functions are objects in Python
# =============================================
# This is the foundation. If you do not understand this,
# decorators will always feel like magic instead of mechanics.


print("=== FUNCTIONS ARE OBJECTS ===")

def greet(name):
    return f"Hello {name}"
    
# Functions can be assigned to variables
say_hello = greet               # NOT calling it - just pointing to it
print(say_hello("Divya"))       # Hello Divya
print(greet is say_hello)       # True - same object, two names

#Functions can be passed as arguements
def run_twice(func, value):
    first = func(value)
    last = func(value)
    return first, last
    
result = run_twice(greet, "Arjun")
print(result)                #('Hello Arjun', 'Hello Arjun')
    # run_twice(greet, "Arjun")
    #         │
    #         ▼
    # func = greet
    # value = "Arjun"

    # first = greet("Arjun")
    #       ↓
    # "Hello, Arjun!"

    # last = greet("Arjun")
    #       ↓
    # "Hello, Arjun!"

    # return (
    #     "Hello, Arjun!",
    #     "Hello, Arjun!"
    # )
    
#Functions can be returned from another function
def make_greeter(greeting):
    def inner(name):
        return f"{greeting} {name}"
    return inner           # returning the function, not calling it   #Thats why no inner()
    
hello = make_greeter("Hello")
namaste = make_greeter("Namaste")
print(hello("Divya"))           # Hello Divya
print(namaste("Arjun"))         # Namaste Arjun


# =============================================
# SECTION 2: What a decorator IS - step by step
# =============================================


print("\n=== WHAT A DECORATOR IS ===")

# A decorator is a function that:
# 1. Takes a function as input
# 2. Returns a NEW function that wraps the orignal
# 3. The wrapper adds the behaviour before and/or after the orignal

#Step 1: write a wrapper manually (no @ needed)
def add_logging(func):
    def wrapper(*args, **kwargs):
        print(f"LOG Calling {func.__name__}")       #Every function in Python automatically has a __name__ attribute
        result = func(*args, **kwargs)
        print(f"[LOG] {func.__name__} returned: {result}")
        print(result)
    return wrapper
    
def calculate_total(price, tax_rate):
    return round(price*(1 + tax_rate), 2)
    
#Manual decoration - wrap the function
logged_calculate = add_logging(calculate_total)
total = logged_calculate(1000, 0.18)

# Print:
# LOG Calling calculate_total
# ↓
# Run:
# calculate_total(1000, 0.18)
# ↓
# Gets:
# 1180.0
# ↓
# Print:
# [LOG] calculate_total returned: 1180.0
# ↓
# Return 1180.0

#Step#2: the @ syntax does exactly the same thing
#@add_logging above def calculate_total is identical to: calculate_total = add_logging(calculate_total)
@add_logging
def calculate_discount(price, percent):
    return round(price*(1-percent/100), 2)

# When Python sees @add_logging, it immediately does:
# calculate_discount = add_logging(calculate_discount)
discount = calculate_discount(1000, 20)

# LOG Calling calculate_discount
# [LOG] calculate_discount returned: 800.0
# 800.0


# =============================================
# SECTION 3: functools.wraps - why it matters
# =============================================


print("\n=== FUNCTOOLS.WRAPS ===")

import functools

# Without functools.wraps:
def bad_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@bad_decorator
def my_test():
    """This test checks login functionality."""
    pass

print(f"Without wraps name: {my_test.__name__}")     # wrapper - WRONG
print(f"Without wraps - doc:  {my_test.__doc__}")    # None - WRONG

# pytest uses __name__ to find and run tests
# if __name__ returns "wrapper", pytest cannot identify your test correctly

# With functools.wraps:
def good_decorator(func):
    @functools.wraps(func)       # copies __name__, __doc__, __module__ from func
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
    
@good_decorator
def my_other_test():
    """This test checks checkout functionality"""
    pass

print(f"With wraps - name: {my_other_test.__name__}")       #With wraps - name: my_other_test
print(f"With wraps - doc: {my_other_test.__doc__}")         #With wraps - doc: This test checks checkout functionality

# RULE: Always use @functools.wraps(func) inside every decorator you write.


# =============================================
# SECTION 4: *args and **kwargs in wrappers
# =============================================

    
print("\n=== *ARGS AND **KWARGS IN WRAPPERS ===")

# Your wrapper must accept ANY arguments the original function accepts.
# You do not know in advance what those are.
# Solution: always use *args, **kwargs in wrapper signature.

import functools

def log_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # args = tuple of positional arguments
        # kwargs = dict of keyword arguments
        print(f"Calling {func.__name__}(args={args}, kwargs = {kwargs})")
        result = func(*args, **kwargs)
        return result
    return wrapper
    
@log_call
def no_args():
    return "no args"
    
@log_call
def one_arg(x):
    return x*2
    
@log_call
def mixed(name, age, role = "tester"):
    return f"{name}, {age}, {role}"

no_args()
one_arg(5)
mixed("Divya", 25, role="sdet")

#Output:
# Calling no_args(args=(), kwargs = {})
# Calling one_arg(args=(5,), kwargs = {})
# Calling mixed(args=('Divya', 25), kwargs = {'role': 'sdet'})