# DAY 5 - FILE 1: Encapsulation and @property
# Run with: python3 encapsulation_property.py

# =============================================
# SECTION 1: Encapsulation — the three levels
# =============================================
# Python does not enforce true private access like Java.
# Instead it uses naming conventions that communicate intent.


print("=== ENCAPSULATION LEVELS ===")

class TestConfig:
    
    def __init__(self, base_url, api_key, timeout = 30):
        self.base_url = base_url    #PUBLIC - anyone can read / write
        self._timeout = timeout     #PROTECTED - internal use, but accessible
        self.__api_key = api_key    #PRIVATE - name-mangled, hard to access
        #Python scans the variable name: It sees the double prefix __ (and no trailing double underscores like __init__).
        # Python automatically renames it in memory: It attaches _ + ClassName to the front
        #The variable is stored as: _TestConfig__api_key.
        
    def get_headers(self):
        #Inside the class, __api_key is accessible normally
        return {"Authorization": f"Bearer{self.__api_key}"}
        
    def update_timeout(self, new_timeout):
        if new_timeout < 1 or new_timeout > 300:
            raise ValueError(f"Timeout must be between 1 and 300, got {new_timeout}")
        self._timeout = new_timeout
    
config = TestConfig("https://staging.api.com", "sk-secret-key-abc123", 30)

#Public - fully accessible
print(config.base_url)      # https://staging.api.com
config.base_url = "https://prod.api.com"    # can set too
print(config.base_url)

#Protected - accessible but the convention says to be careful
print(config._timeout)              # 30 - works but you're breaking convention
config._timeout = 60                # works but shouldn't do this from outside

#Private - name-mangled to _TestConfig__api_key
try:
    print(config.__api_key)     # AttributeError
except AttributeError as e:
    print(f"Can't access __api_key directly : {e}")
    
#Can still access if you know the mangled name - Python isnt truly private
print(config._TestConfig__api_key)      # works - but you're deliberately breaking it
print(config.get_headers())     #Correct way - use the public method


# =============================================
# SECTION 2: @property — computed attributes
# =============================================


print("\n=== @PROPERTY ===")

class APITestResult:
    def __init__(self, endpoint, status_code, response_time_ms, response_body):
        self.endpoint = endpoint
        self.status_code = status_code
        self.response_time_ms = response_time_ms
        self.response_body = response_body
        self._notes = []
        
    # @property makes this look like an attribute but runs code
    @property
    def passed(self):
        return 200 <= self.status_code < 300
        
    @property
    def is_fast(self):
        return self.response_time_ms < 500
        
    @property
    def status_label(self):
        if self.status_code == 200:
            return "OK"
        elif self.status_code == 201:
            return "Created"
        elif self.status_code == 404:
            return "Not Found"
        elif self.status_code >= 500:
            return "Server Error"
        else:
            return f"HTTP {self.status_code}"
            
    @property
    def summary(self):
        outcome = "PASS" if self.passed else "FAIL"
        speed = "fast" if self.is_fast else "slow"
        return f"{outcome} | {self.status_label} | {self.response_time_ms}ms ({speed})"
    # property with a setter
    @property
    def notes(self):
        return self._notes
    
    @notes.setter
    def notes(self, value):
        if not isinstance(value, list):
            raise TypeError("Notes must be a list")
        self._notes = value

    def __str__(self):
        return f"APITestResult({self.endpoint}: {self.summary})"


result1 = APITestResult("/users/1", 200, 234, {"id": 1, "email": "a@b.com"})
result2 = APITestResult("/orders", 500, 1203, {"error": "Internal Server Error"})
result3 = APITestResult("/users/999", 404, 89, {})

#Properties look like attributes - no () needed
print(result1.passed)           # True
print(result1.is_fast)          # True
print(result1.status_label)     # OK
print(result1.summary)          # PASS | OK | 234ms (fast)
print(result1)      #APITestResult(/users/1: PASS | OK | 234ms (fast))  i.e prints __str__

print(result2.passed)           # False
print(result2.summary)          # FAIL | Server Error | 1203ms (slow)

print(result3.passed)           # False
print(result3.summary)          # FAIL | Not Found | 89ms (fast)

# Setter
result1.notes = ["Tested in staging", "Passed schema validation"]
print(result1.notes)

try:
    result1.notes = "should be a list"  # TypeError
except TypeError as e:
    print(f"TypeError: {e}")

# Cannot set read-only property
try:
    result1.passed = True       # AttributeError - no setter defined i.e passed was created using only @property (a getter), but no @passed.setter was defined for it. Because there is no setter method, Python refuses to allow direct assignment
except AttributeError as e:
    print(f"Cannot set read-only property: {e}")
    

# =============================================
# SECTION 3: Why @property beats public attributes
# =============================================


print("\n=== PROPERTY VS ATTRIBUTE ===")

# Bad design: expose raw attribute
class BadResult:
    def __init__(self, status_code):
        self.passed = status_code == 200  # stored as bool

# Problem: if status_code changes later, passed is stale
r = BadResult(200)
print(r.passed)     # True
r.status_code = 404  # whoops, forgot to update passed
# r.passed is still True even though status is now 404

# Good design: @property computes from current state
class GoodResult:
    def __init__(self, status_code):
        self.status_code = status_code

    @property
    def passed(self):
        return self.status_code == 200  # always current

r2 = GoodResult(200)
print(r2.passed)        # True
r2.status_code = 404    # update the source
print(r2.passed)        # False - automatically correct