# DAY 8 - FILE 1: How Context Managers Actually Work
# Run with: python3 context_manager_fundamentals.py


# =============================================
# SECTION 1: The problem context managers solve
# =============================================


print("=== THE PROBLEM CONTEXT MANAGERS SOLVE ===")

# BAD: manual resource management
# If an exception happens between open and close,
# the file never gets closed. Memory leak. File lock held forever.

def bad_file_write():
    # Open (or create) the file "temp.txt" in write mode ("w").
    # If the file already exists, its contents are erased.
    # The returned file object is stored in the variable 'f'.
    f = open("temp.txt", "w")
    f.write("some data")
    # imagine an exception here
    # f.close() NEVER runs
    f.close()
    
# GOOD: "with" statement guarantees cleanup
def good_file_write():
    with open ("temp.txt", "w") as f:
        f.write("some data")
        # exception here? doesn't matter.
        # f.close() ALWAYS runs when the with block exits
        
good_file_write()
import os
os.remove("temp.txt")

# The with statement calls two special methods:
# __enter__: runs when entering the with block, returns the resource
# __exit__:  runs when leaving the with block (success OR exception)


# =============================================
# SECTION 2: What with actually does step by step
# =============================================
    
    
print("\n=== WHAT WITH ACTUALLY DOES ===")

class Explainer:
    """Demonstrates exactly what Python calls and when"""
    
    def __enter__(self):
        print(" 1. __enter__ called - setup runs here")
        print(" 2. return value goes to the 'as' variable")
        return "I am the resource"      # this is what 'as x' receives
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f" 4. __exit__ called - cleanup runs here")
        print(f"     exc_type: {exc_type}")   # None if no exception
        print(f"     exc_val:  {exc_val}")    # None if no exception
        print(f"     exc_tb:   {exc_tb}")     # None if no exception
        # Return False (or None) = do NOT supress the exception
        # Return True             = suppress the exception (swallow it)
        return False        #I handled cleanup, but do not hide the error. Let Python raise it normally
        
print ("---Normal exit---")
with Explainer() as resource:
    print(f" 3. Inside the block, resource = '{resource}'")
# __exit__ is called with exc_type=None because no exception
        
print("\n--- Exit via exception ---")
try:
    with Explainer() as resource:
        print(f" 3. Inside with block, about to raise")
        raise ValueError("something went wrong")
        print("  This never runs")
except ValueError as e:
    print(f" 5. Exception propogated: {e}")
# __exit__ is called with exc_type=ValueError, then exception propagates
        
print("\n--- Suppressing an exception ---")

class Supressor:
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type is ValueError:
            print("  Suppressing ValueError")
            return True     #True - swallows the error
        return False        #False - let other exceptions propogated
    
with Supressor() as resource:
    raise ValueError("This will be swallowed")
print("  Execution continues after suppressed exception")


# =============================================
# SECTION 3: Why finally matters
# =============================================


print("\n=== WHY FINALLY MATTERS ===")

#Finally runs NO MATTER WHAT - success, exception and return

def demonstrate_finally():
    print(" try block starts")
    try:
        print(" doing work")
        # comment out the next line to see success path
        raise RuntimeError("Something broke")
        print(" this never runs if exception raised")
    except RuntimeError as e:
        print(f" except block: caught {e}")
    finally:
        print(" finally block: ALWAYS runs")
        print(" this is where cleanup goes")

demonstrate_finally()
# finally vs __exit__ - they solve the same problem
# finally: when you know exactly what to clean up right here
# __exit__: when you want a reusable cleanup pattern across many places

# The critical case: exception inside except block   
print("\n---finally survives exception in except---")
def tricky():
    try:
        raise ValueError("first error")
    except ValueError:
        print(" in except block")
        raise RuntimeError("second error in except!")       #new exception
    finally:
        print(" finally rus even when except raises")       #still runs
        
try:
    tricky()
except RuntimeError as e:
    print(f"  outer caught: {e}")
    
    
# =============================================
# SECTION 4: __enter__ and __exit__ signatures
# =============================================


print("\n=== ENTER AND EXIT SIGNATURES ===")

# __exit__ receives three arguments about any exception:
# exc_type: the exception CLASS (e.g. ValueError, None if no exception)
# exc_val:  the exception INSTANCE (the actual error object)
# exc_tb:   the traceback object

# Common pattern: handle specific exceptions, let others propagate
class SelectiveHandler:
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            print(" No exception - normal cleanup")
            return False            #False does not matter here because there is no exception to suppress.
            
        if exc_type is ValueError:
            print(f" Handling ValueError: {exc_val}")   
            return True         # suppress it
        
        if exc_type is ConnectionError:
            print(f"  Logging ConnectionError: {exc_val}")
            # log it but let it propagate
            return False
            
        # Unknown exception - let it propagate
        print(f" Unknown exception: {exc_type.__name__}: {exc_val}")
        return False        #I cleaned up resources (close browser, release connection, save logs), but the test should still fail
        
with SelectiveHandler():
    raise ValueError("handled and supressed")
print("Excution continues")

try:
    with SelectiveHandler():
        raise ConnectionError("logged but propogated")
except ConnectionError:
    print("ConnectionError propagated as expected")