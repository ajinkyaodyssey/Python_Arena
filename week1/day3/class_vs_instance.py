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

class APIClient:
    _base_url = "https://api.example.com"
    _instance_count = 0
    
    def __init__(self, api_key, version = "v1"):
        self.api_key = api_key
        self.version = version
        self.request_count = 0
        APIClient._instance_count += 1
        
    #INSTANCE METHOD - needs self and works on a specific object
    def get(self, endpoint):
        self.request_count+=1
        url = f"{self._base_url}/api/{self.version}{endpoint}"
        return f"GET {url} (request #{self.request_count})"
        
    #CLASS METHOD - needs cls, works on the class itself
    #Use for: alternative constructors, factory methods
    @classmethod
    def from_env(cls):
        import os
        key = os.getenv("API_KEY", "default-test-key")
        return cls(key)     #cls() is same as APIClient()
        
    @classmethod
    def get_instance_count(cls):
        return cls._instance_count
        
    #STATIC METHOD - needs neither self nor cls
    #Use for: utility functions that belongs to the class conceptully but dont need class or instance data
    
    @staticmethod
    def is_valid_endpoint(endpoint):
        return endpoint.startswith("/") and len(endpoint) > 1
    
    @staticmethod
    def build_auth_header(api_key):
        return {"Authorization" : f"Bearer {api_key}"}
        
# Instance method - needs an object
client1 = APIClient("key-abc-123")
client2 = APIClient("key-xyz-789", version="v2")

print(client1.get("/users"))
print(client1.get("/orders"))   # request_count increments on client1
print(client2.get("/users"))    # client2 starts at 1 - independent
    
# Class method - called on class OR instance
client3 =  APIClient.from_env()
print(f"Created from env: {client3.api_key}")
print(f"Total instances: {APIClient.get_instance_count()}")  # 3

#Static method - no class, no object needed
print(f"\nValid endpoint '/users': {APIClient.is_valid_endpoint('/users')}")     #Valid endpoint '/users': True   
print(f"Valid endpoint 'users': {APIClient.is_valid_endpoint('users')}")        #Valid endpoint 'users': False
print(f"Auth header: {APIClient.build_auth_header('my-key')}")      #Auth header: {'Authorization': 'Bearer my-key'}


# =============================================
# SECTION 3: The @property decorator
# =============================================


print("\n=== @PROPERTY ===")

class TestResult:
    def __init__(self, name, passed, failed):
        self.name = name
        self._passed = passed    # _ signals "don't set this directly"
        self._failed = failed    # _ signals "don't set this directly"
        
    @property
    def passed(self):
        return self._passed
        
    @property
    def failed(self):
        return self._failed
        
    @property
    def total(self):
        # Computed from other values - no need to store separately
        return self._passed + self._failed
        
    @property
    def pass_rate(self):
        if self.total == 0:
            return 0.0
        return round((self._passed / self.total)*100, 1)
    
    @property
    def status(self):
        if self._failed == 0:
            return "ALL PASS"
        elif self._passed == 0:
            return "ALL FAIL"
        else:
            return "PARTIAL"
            
    def __str__(self):
        return (f"TestResult({self.name}: "
                f"{self.passed}P/{self.failed}F "
                f"= {self.pass_rate}% | {self.status})")
        
result = TestResult("smoke_suite", passed=18, failed=2) 
print(result)
print(f"Total: {result.total}")       # computed - no stored attribute
print(f"Pass rate: {result.pass_rate}%")
print(f"Status: {result.status}")

# Properties look like attributes but run code
# result.total   calls the total() function
# result.total = 5  would raise AttributeError (no setter defined)
try:
    result.total = 25
except AttributeError as e:
    print(f"Cannot set computed property: {e}")