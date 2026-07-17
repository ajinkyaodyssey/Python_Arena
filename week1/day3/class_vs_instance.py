# DAY 3 - FILE 2: Class vs Instance Attributes and Methods
# Run with: python3 class_vs_instance.py
# This is the most commonly asked OOP topic in interviews


# =============================================
# SECTION 1: Class attributes vs Instance attributes
# =============================================


print("=== CLASS VS INSTANCE ATTRIBUTES ===")

class TestSuite:
    # Class attribute: defined on the class itself
    # Shared by all instances - one value for everyone
    default_timeout = 30
    support_browsers = ["chromium", "firefox", "webkit"]
    _suite_count = 0        #convention _ means internal use
    
    def __init__ (self, name, browser = "chromium"):
        # Instance attributes - unique to EACH object
        self.name = name
        self.browser = browser
        self.tests = []
        self.passed = 0
        self.failed = 0
        TestSuite._suite_count+=1       # increment class-level counter

    def add_test(self, test_name):
        self.tests.append(test_name)
        
    def get_summary(self):
        return {
            "name": self.name,
            "browser": self.browser,
            "total": len(self.tests),
            "timeout": self.default_timeout
        }
    
suite1 = TestSuite("smoke_suite")
suite2 = TestSuite("regression_suite", browser="firefox")

#Instance attributes are independent
suite1.add_test("login_test")
suite1.add_test("checkout_test")
suite2.add_test("full_flow_test")

print(f"suite1 tests: {suite1.tests}")   # ['login_test', 'checkout_test']
print(f"suite2 tests: {suite2.tests}")   # ['full_flow_test'] - independent

# Class attributes are shared
print(f"\nDefault timeout via suite1: {suite1.default_timeout}")    # 30
print(f"Default timeout via suite2: {suite2.default_timeout}")      # 30
print(f"Default timeout via class:  {TestSuite.default_timeout}")   # 30

#Changing class attributes: affects all instances
TestSuite.default_timeout = 60
print(f"\nDefault timeout via suite1: {suite1.default_timeout}")    # 60
print(f"Default timeout via suite2: {suite2.default_timeout}")      # 60
print(f"Default timeout via class:  {TestSuite.default_timeout}")   # 60

#BUT if you set it on an instance, it creates an instance attribute
#That SHADOWS the class attribute for that instance only
suite1.default_timeout = 90     # creates instance attribute on suite1
print(f"\nAfter setting on suite1 only:")
print(f"suite1.default_timeout: {suite1.default_timeout}")  # 90 - instance attr
print(f"suite2.default_timeout: {suite2.default_timeout}")  # 60 - still class attr
print(f"TestSuite.default_timeout: {TestSuite.default_timeout}")  # 60 - class attr

print(f"Total test suites created: {TestSuite._suite_count}")


# =============================================
# SECTION 2: Instance vs Class vs Static methods
# =============================================


print("\n=== INSTANCE VS CLASS VS STATIC METHODS ===")

