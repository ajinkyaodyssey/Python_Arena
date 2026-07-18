# DAY 3 - FILE 3: Dunder (Magic) Methods
# Run with: python3 dunder_methods.py
# These are what make your objects behave like built-in types


print("=== DUNDER METHODS ===")

class TestRun:
    def __init__(self, name, tests = None):
        self.name = name
        self.tests = tests or []        # never use [] as default argument - explained below
    #__str__ :called by print() and str() - for humans
    def __str__(self):
        return f"TestRun('{self.name}', {len(self.tests)} tests)"
        
    # __repr__: called by debugger, inside containers - for developers
    def __repr__(self):
        return f"TestRun(name = {self.name!r}, tests = {self.tests!r})"
        
    #__len__: called by len() 
    def __len__(self):
        return len(self.tests)
    
    #__contains__: called by 'in' operator
    def __contains__(self, test_name):
        return test_name in self.tests
        
    #__iter__: makes the object iterable (for loops work on it)
    def __iter__(self):
        return iter(self.tests)
        
    #__getitem__: called by [] indexing
    def __getitem__(self, index):
        return self.tests[index]
        
    #__eq__: called by == operator
    def __eq__(self, other):
        if not isinstance(other, TestRun):
            return NotImplemented
        return self.name == other.name and self.tests == other.tests
        
    #__bool__: called by if statement and bool()
    def __bool__(self):
        return len(self.tests) > 0
        
    def add(self, test_name):
        self.tests.append(test_name)
        return self     # enables chaining: run.add("a").add("b")
        
run1 = TestRun("smoke", ["login", "logout", "checkout"])
run2 = TestRun("empty")
run3 = TestRun("smoke", ["login", "logout", "checkout"])

#str
print(str(run1))        #TestRun('smoke', 3 tests)
print(run1)             #TestRun('smoke', 3 tests)  # same - print calls __str__

#__repr__
print(repr(run1))       #TestRun(name = 'smoke', tests = ['login', 'logout', 'checkout'])
print([run1, run2])     # list uses __repr__ for each item

# __len__
print(f"\nlen(run1): {len(run1)}")  # 3
print(f"len(run2): {len(run2)}")    # 0

# __contains__
print(f"\n'login' in run1: {'login' in run1}")      # True
print(f"'refund' in run1: {'refund' in run1}")      # False

# __iter__
print("\nIterating")
for test in run1:       #associated with tests when we defined __iter__
    print(f"  {test}")      #login  logout  checkout
        
#__getitem__
print(f"\nrun1[0] = {run1[0]}")     #login
print(f"run1[-1] = {run1[-1]}")     #checkout

#__eq__
print(f"\nrun1 == run3: {run1 == run3}")    # True - same name and tests
print(f"run1 == run2: {run1 == run2}")    # False

# __bool__
print(f"\nbool(run1): {bool(run1)}")    # True - has tests
print(f"bool(run2): {bool(run2)}")    # False - empty

if run1:
    print("run1 has tests - will execute")
if not run2:
    print("run2 is empty - skip")
    
# Method chaining via return self
run2.add("test_a").add("test_b").add("test_c")
print(f"\nrun2 after chaining: {run2}")


# =============================================
# WHY NOT [] AS DEFAULT ARGUMENT - IMPORTANT
# =============================================


print("\n=== MUTABLE DEFAULT ARGUMENT BUG ===")

# WRONG - this is a classic Python bug
def wrong_add_test(test_name, test_list=[]):   # [] created ONCE at definition
    test_list.append(test_name)
    return test_list

r1 = wrong_add_test("login")
r2 = wrong_add_test("checkout")    # BUG: shares the same list as r1
print(f"r1: {r1}")     # ['login', 'checkout'] - WRONG, expected ['login']
print(f"r2: {r2}")     # ['login', 'checkout'] - WRONG, expected ['checkout']

#CORRECT
def correct_add_test(test_name, test_list = None):
    if test_list is None:
        test_list = []  # new list created fresh each call
    test_list.append(test_name)
    return test_list
    
r3 = correct_add_test("login")
r4 = correct_add_test("checkout")
print(f"r3: {r3}")     # ['login']    - correct
print(f"r4: {r4}")     # ['checkout'] - correct