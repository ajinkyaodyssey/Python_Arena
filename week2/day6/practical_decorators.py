# DAY 6 - FILE 2: Practical Decorators for Test Automation
# Run with: python3 practical_decorators.py

import functools
import time


# =============================================
# SECTION 1: @timer decorator
# =============================================


print("=== @TIMER ===")

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()     #high-resolution counter
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f" [{func.__name__}] took {elapsed:.4f}s")
        return result
    return wrapper
    
@timer
def fetch_users():
    time.sleep(0.1)     #simulating API call
    return [{"id": 1}, {"id": 2}, {"id": 3}]
    
@timer
def run_all_tests():
    time.sleep(0.2)     #simulating test suite
    return {"passed": 18, "failed": 2}
    
users = fetch_users()           # [fetch_users] took 0.1001s
results = run_all_tests()       # [run_all_tests] took 0.2001s
print(f"Users: {users}")        # Users: [{'id': 1}, {'id': 2}, {'id': 3}]
print(f"Results: {results}")    #Results: {'passed': 18, 'failed': 2}

    
# =============================================
# SECTION 2: @retry decorator
# =============================================


print("\n=== @RETRY ===")

import random

def retry(max_attempts = 3, delay = 0.1, exceptions = (Exception,)):
    """
    Decorator with arguements.
    Note the extra layer of retry() return decorator which returns the wrapper.
    retry (3,0.5) -> decorator -> wrapper -> orignal functional call.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    print(f" Attempt {attempt}/{max_attempts}: {func.__name__}")
                    result = func(*args, **kwargs)
                    print(f" SUCCESS on attempt {attempt}")
                    return result
                except Exception as e:
                    last_exception = e
                    print(f" Failed: {e}")
                    if attempt < max_attempts:
                        time.sleep(delay)
            print(f" All {max_attempts} attempts failed")
            raise last_exception
        return wrapper
    return decorator
    
# Simulate a flaky API that fails randomly
call_count = 0

@retry(max_attempts = 3, delay = 0.05)
def flaky_api_call():
    global call_count
    call_count+=1
    if call_count<3:    # fails first 2 times, succeeds on 3rd
        raise ConnectionError(f"Network timeout (call #{call_count})")
    return {"status": "success", "data": [1,2,3]}
    
result = flaky_api_call()
print(f"Final result: {result}")
        
# Retry only specific exceptions
@retry(max_attempts=2, delay=0.05, exceptions=(ValueError,))
def validate_response(data):
    if not data:
        raise ValueError("Empty response")
    return data

try:
    validate_response({})       # empty dict is falsy
except ValueError as e:
    print(f"\nCaught after all retries: {e}")
    

# =============================================
# SECTION 3: Decorators with and without arguments
# =============================================


print("\n=== DECORATOR WITH VS WITHOUT ARGUMENTS ===")

# WITHOUT arguments - simpler, one less layer
def simple_log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f" Calling {func.__name__}")            
        return func(*args, **kwargs)
    return wrapper
    
@simple_log
def my_test():
    return "pass"
    
my_test()

# WITH arguments - needs extra layer
def log_with_level(level = "INFO"):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            print(f" [{level}] Calling {func.__name__}")
            return func(*args, **kwargs)
        return wrapper
    return decorator
    
@log_with_level(level="DEBUG")
def debug_test():
    return "pass"
    
@log_with_level(level="DEBUG")
def debug_test():
    return "pass"

@log_with_level(level="WARNING")
def warning_test():
    return "pass"

debug_test()
warning_test()

# The pattern is always:
# No args:   decorator(func) -> wrapper
# With args: outer(args) -> decorator(func) -> wrapper


# =============================================
# SECTION 4: Stacking multiple decorators
# =============================================


print("\n=== STACKING DECORATORS ===")

# Multiple decorators apply bottom-up
# @timer
# @simple_log
# def my_func()
# is the same as: my_func = timer(simple_log(my_func))
# simple_log wraps first, then timer wraps that

@timer
@simple_log
def checkout_flow():
    time.sleep(0.05)
    return "checkout complete"

result = checkout_flow()
# simple_log fires (inner wrapper)
# timer fires around simple_log (outer wrapper)
print(f"Result: {result}")

#Output:
#  Calling checkout_flow
#  [checkout_flow] took 0.0501s
    

# =============================================
# SECTION 5: Real-world test automation decorators
# =============================================


print("\n=== REAL AUTOMATION DECORATORS ===")

# Track test execution metadata
test_registry = []

def register_test(category="general"):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            status = "PASS"
            error = None
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                status = "FAIL"
                error = str(e)
                result = None
            duration = time.perf_counter() - start
            test_registry.append({
                "name": func.__name__,
                "category": category,
                "status": status,
                "duration_ms": round(duration*1000,2),
                "error": error
            })
        return wrapper
    return decorator

@register_test(category="auth")
def test_login_valid():
    time.sleep(0.02)
    assert True     #"check that this condition is True. "True is always true, the assertion always passes and nothing happens.

@register_test(category="auth")
def test_login_invalid():
    time.sleep(0.01)
    assert True

@register_test(category="checkout")
def test_checkout_fails():
    time.sleep(0.01)
    raise AssertionError("Checkout button not found")
    
# Run all tests
for test_fn in [test_login_valid, test_login_invalid, test_checkout_fails]:
    test_fn()

# Show results
print("\nTest Registry:")
for entry in test_registry:
    icon = "PASS" if entry["status"] == "PASS" else "FAIL"
    print(f"  [{icon}] {entry['name']} ({entry['category']}) "
          f"- {entry['duration_ms']}ms"
          f"{' | ' + entry['error'] if entry['error'] else ''}")