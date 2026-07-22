# DAY 5 - FILE 2: Abstract Classes, @classmethod, @staticmethod
# Run with: python3 abstract_classmethod_staticmethod.py

from abc import ABC, abstractmethod
import os
from datetime import datetime


# =============================================
# SECTION 1: Abstract Classes in depth
# =============================================


print("=== ABSTRACT CLASSES ===")

class BaseAPIClient(ABC):
    """
    Abstract base for all API clients in the framework.
    Any subclass MUST implement: authenticate(), get(), post()
    If it doesn't, Python raises TypeError at instantiation.
    This catches missing implementations at the start of a test run,
    not buried inside a test at 2am.
    """
    
    def __init__(self, base_url):
        self.base_url = base_url
        self._session_token = None
        self._request_count = 0
        
    @abstractmethod
    def authenticate(self, credentials):
        """Subclass decides HOW to authenticate."""
        pass
    
    @abstractmethod
    def get(self, endpoint, **kwargs):
        """Subclass decides HOW to make GET requests."""
        pass
    
    @abstractmethod
    def post(self, endpoint, payload, **kwargs):
        """Subclass decides HOW to make POST requests."""
        pass
    
    #Concrete methods - shared by all subclasses
    def is_authenticated(self):
        return self._session_token is not None
        
    def get_request_count(self):
        return self._request_count
        
    def _increment_count(self):
        self._request_count+=1
    
    def __str__(self):
        auth ="authenticated" if self.is_authenticated() else "not authenticated"
        return f"{self.__class__.__name__}({self.base_url} | {auth})"
        
        
class MockAPIClient(BaseAPIClient):
    """Concrete implementation for testing - returns mocked responses."""
    
    def authenticate(self, credentials):
        if credentials.get("api_key") == "valid-key":
            self._session_token = "mock-token-abc123"
            return True
        return False
        
    def get(self, endpoint, **kwargs):
        self._increment_count()
        return {
            "status_code" : 200,
            "body": {"endpoint": endpoint, "method": "GET", "mock": True}
        }
        
    def post(self, endpoint, payload, **kwargs):
        self._increment_count()
        return {
            "status_code": 201,
            "body": {"id": 999, "endpoint": endpoint, "data": payload}
        }

## Cannot instantiate abstract class  i.e.   Abstract Base Class is a blueprint, not a fully finished class, so Python refuses to let you create an instance (object) of it.
try:    
    client = BaseAPIClient("https://api.com")
except TypeError as e:
    print(f"Cannot instantiate ABC: {e}")
    
#Can instantiate concrete class
mock = MockAPIClient("https://staging.api.com")
mock.authenticate({"api_key": "valid-key"})
print(mock)

resp  = mock.get("/users/1")
print(f"GET response: {resp}")

resp = mock.post("/users", {"name": "Divya", "role": "sdet"})
print(f"POST response: {resp}")
print(f"Total requests: {mock.get_request_count()}")


# =============================================
# SECTION 2: @classmethod deep dive
# =============================================


print("\n=== @CLASSMETHOD ===")

class TestEnvironment:
    _environments = {
        "staging": {
            "base_url": "https://staging.saucedemo.com",
            "api_url": "https://api-staging.saucedemo.com",
            "headless": True,
            "timeout": 30
        },
        "production": {
            "base_url": "https://www.saucedemo.com",
            "api_url": "https://api.saucedemo.com",
            "headless": True,
            "timeout": 45
        },
        "local": {
            "base_url": "http://localhost:3000",
            "api_url": "http://localhost:8080",
            "headless": False,
            "timeout": 60
        }
    }
    
    def __init__(self, name, base_url, api_url, headless, timeout):
        self.name = name
        self.base_url = base_url
        self.api_url = api_url
        self.headless = headless
        self.timeout = timeout
        
    # @classmethod: alternate constructor - creates instance from env name
    # cls = the class itself (TestEnvironment)
    # This lets you do: env = TestEnvironment.from_name("staging")
    # instead of manually passing all 5 arguments every time
    @classmethod
    def from_name(cls, env_name):
        if env_name not in cls._environments:
            raise ValueError(
                f"Unknown environment: {env_name}. "
                f"Available: {list(cls._environments.keys())}"
            )
        cfg = cls._environments[env_name]
        return cls(
            name=env_name,
            base_url=cfg["base_url"],
            api_url=cfg["api_url"],
            headless=cfg["headless"],
            timeout=cfg["timeout"]
        )

    # @classmethod: factory that reads from environment variable
    @classmethod
    def from_env_var(cls):
        env_name = os.getenv("TEST_ENV", "staging")
        return cls.from_name(env_name)

    # @classmethod: utility on the class, not an instance
    @classmethod
    def list_available(cls):
        return list(cls._environments.keys())

    def __str__(self):
        return (f"TestEnvironment({self.name} | "
                f"url={self.base_url} | headless={self.headless})")


# Using class methods - no instance needed to create the instance
staging = TestEnvironment.from_name("staging")
local = TestEnvironment.from_name("local")

print(staging)
print(local)
print(f"Available environments: {TestEnvironment.list_available()}")

try:
    bad = TestEnvironment.from_name("dev")
except ValueError as e:
    print(f"ValueError: {e}")
    
    
# =============================================
# SECTION 3: @staticmethod deep dive
# =============================================


print("\n=== @STATICMETHOD ===")

class TestDataValidator:
    """
    Collection of validation utilities.
    None of these need self or cls - they're pure functions
    that logically belong in this class.
    Static methods = utility functions with a home.
    """

    @staticmethod
    def is_valid_email(email):
        if not email or "@" not in email:
            return False
        parts = email.split("@")
        return len(parts) == 2 and "." in parts[1] and len(parts[1]) > 2

    @staticmethod
    def is_valid_status_code(code):
        return isinstance(code, int) and 100 <= code <= 599

    @staticmethod
    def is_valid_url(url):
        return url.startswith(("http://", "https://")) and len(url) > 10

    @staticmethod
    def sanitise_test_name(name):
        """Convert any string to a valid test name."""
        return name.lower().replace(" ", "_").replace("-", "_")

    @staticmethod
    def mask_sensitive(value, visible_chars=4):
        """Mask a secret value for logging - show only last N chars."""
        if len(value) <= visible_chars:
            return "*" * len(value)
        return "*" * (len(value) - visible_chars) + value[-visible_chars:]

    @staticmethod
    def parse_duration(duration_str):
        """Parse '1.23s' or '456ms' into milliseconds."""
        duration_str = duration_str.strip()
        if duration_str.endswith("ms"):
            return float(duration_str[:-2])
        elif duration_str.endswith("s"):
            return float(duration_str[:-1]) * 1000
        raise ValueError(f"Cannot parse duration: {duration_str}")


# Static methods - call on class, no instance needed
print(TestDataValidator.is_valid_email("divya@test.com"))       # True
print(TestDataValidator.is_valid_email("divya@test"))           # False
print(TestDataValidator.is_valid_email(""))                     # False

print(TestDataValidator.is_valid_status_code(200))              # True
print(TestDataValidator.is_valid_status_code(999))              # False

print(TestDataValidator.sanitise_test_name("Login Test - Happy Path"))
# login_test___happy_path

print(TestDataValidator.mask_sensitive("sk-secret-key-abc123"))
# ********************3
print(TestDataValidator.mask_sensitive("sk-secret-key-abc123", visible_chars=8))

print(TestDataValidator.parse_duration("1.23s"))    # 1230.0
print(TestDataValidator.parse_duration("456ms"))    # 456.0

# Can also call on instance but that's unusual
validator = TestDataValidator()
print(validator.is_valid_email("test@example.com"))  # works but call on class instead