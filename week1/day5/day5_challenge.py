# DAY 5 - FILE 3: Challenge
# Extend the page hierarchy with abstract classes,
# @property, @classmethod, @staticmethod
# Run with: python3 day5_challenge.py

from abc import ABC, abstractmethod

# =============================================
# INSTRUCTIONS
# =============================================
#
# CLASS 1: BasePage(ABC)
#   Make BasePage abstract this time.
#   Class attributes:
#     - DEFAULT_TIMEOUT = 30_000
#     - SUPPORTED_BROWSERS = ["chromium", "firefox", "webkit"]
#   __init__(self, page, base_url, browser="chromium"):
#     - self.page = page
#     - self.base_url = base_url
#     - self._browser = browser
#     - self._loaded = False
#     - self._action_log = []
#     - self._load_time_ms = None
#   Abstract methods (subclasses MUST implement):
#     - goto(self)
#     - get_title(self)
#   Concrete methods (shared by all):
#     - navigate(path="")
#         appends f"navigate:{self.base_url}{path}" to _action_log
#         sets _loaded = True
#         returns self
#     - is_loaded()   returns self._loaded
#     - get_action_log()   returns self._action_log
#     - take_screenshot(name)
#         appends f"screenshot:{name}" to _action_log
#         returns f"{name}.png"
#   Properties:
#     - browser (read-only)
#         returns self._browser
#     - load_time_ms (read + write)
#         getter: returns self._load_time_ms
#         setter: raises ValueError if value < 0
#                 sets self._load_time_ms = value
#     - is_fast (read-only)
#         returns True if _load_time_ms is not None and < 1000
#         returns False otherwise
#   Class methods:
#     - create(cls, page, base_url, browser="chromium")
#         validates browser is in SUPPORTED_BROWSERS
#         raises ValueError if not
#         returns cls(page, base_url, browser)
#   Static methods:
#     - is_valid_url(url)
#         returns True if url starts with "http://" or "https://"
#         returns False otherwise
#     - sanitise_name(name)
#         returns name.lower().strip().replace(" ", "_")
#
# CLASS 2: LoginPage(BasePage)
#   PATH = "/login"
#   __init__(self, page, base_url, browser="chromium"):
#     - super().__init__(page, base_url, browser)
#     - self._username = None
#     - self._password = None
#     - self.failed_attempts = 0
#   Implement abstract methods:
#     - goto()
#         calls navigate(PATH), returns self
#     - get_title()
#         returns "Login Page"
#   Other methods:
#     - login(username, password)
#         appends f"login:{username}" to _action_log
#         sets self._username = username
#         if username=="standard_user" and password=="secret_sauce":
#             returns True
#         else:
#             self.failed_attempts += 1
#             returns False
#   Properties:
#     - current_user (read-only)
#         returns self._username if set, else "anonymous"
#     - is_authenticated (read-only)
#         returns True if _username=="standard_user", False otherwise
#   Static methods:
#     - is_valid_credentials(username, password)
#         returns True if both are non-empty strings
#         returns False otherwise
#   __str__:
#     returns f"LoginPage(user={self.current_user} | auth={self.is_authenticated})"
#
# CLASS 3: CheckoutPage(BasePage)
#   PATH = "/checkout-step-one.html"
#   __init__(self, page, base_url, browser="chromium"):
#     - super().__init__(page, base_url, browser)
#     - self._first_name = None
#     - self._last_name = None
#     - self._postal_code = None
#     - self._order_complete = False
#   Implement abstract methods:
#     - goto()
#         calls navigate(PATH), returns self
#     - get_title()
#         returns "Checkout Page"
#   Other methods:
#     - fill_details(first_name, last_name, postal_code)
#         validates each field is a non-empty string
#         raises ValueError("All fields required") if any is empty/None
#         sets self._first_name, self._last_name, self._postal_code
#         appends f"fill:{first_name}:{last_name}:{postal_code}" to _action_log
#         returns self
#     - complete_order()
#         if form not complete: raise ValueError("Complete form first")
#         sets self._order_complete = True
#         appends "order_complete" to _action_log
#         returns "Order placed successfully"
#   Properties:
#     - is_form_complete (read-only)
#         returns True only if all three name/postal fields are set (not None)
#     - order_status (read-only)
#         returns "complete" if _order_complete else "pending"
#   __str__:
#     returns f"CheckoutPage(form={self.is_form_complete} | order={self.order_status})"


class BasePage(ABC):
    DEFAULT_TIMEOUT = 30_000
    SUPPORTED_BROWSERS = ["chromium", "firefox", "webkit"]
    
    def __init__(self, page, base_url, browser="chromium"):
        self.page = page
        self.base_url = base_url
        self._browser = browser
        self._loaded = False
        self._action_log = []
        self._load_time_ms = None
        
    @abstractmethod
    def goto(self):
        pass
    
    @abstractmethod
    def get_title(self):
        pass
    
    #Concrete methods
    def navigate(self, path=""):
        self._action_log.append(f"navigate:{self.base_url}{path}")
        self._loaded = True
        return self
    
    def is_loaded(self):
        return self._loaded
    
    def get_action_log(self):
        return self._action_log
        
    def take_screenshot(self, name):
        self._action_log.append(f"screenshot:{name}")
        return f"{name}.png"
        
    @property
    def browser(self):
        return self._browser 
    
    @property
    def load_time_ms(self):
        return self._load_time_ms
        
    @load_time_ms.setter
    def load_time_ms(self, value):
        if value < 0:
            raise ValueError
        self._load_time_ms = value
        
    @property
    def is_fast(self):
        if self._load_time_ms is not None and self._load_time_ms < 1000:
            return True
        else:
            return False
            
    @classmethod
    def create(cls, page, base_url, browser="chromium"):
        if browser not in cls.SUPPORTED_BROWSERS:
            raise ValueError
        return cls(page, base_url, browser)
            
    @staticmethod
    def is_valid_url(url):
        if url.startswith("http://") or url.startswith("https://"):
            return True
        else:
            return False
    
    @staticmethod
    def sanitise_name(name):
        return name.lower().strip().replace(" ", "_")

class LoginPage(BasePage):
    PATH = "/login"
    
    def __init__(self, page, base_url, browser="chromium"):
        super().__init__(page, base_url, browser)
        self._username = None
        self._password = None
        self.failed_attempts = 0
        
    def goto(self):
        self.navigate(LoginPage.PATH)
        return self
        
    def get_title(self):
        return "Login Page"
        
    def login(self, username, password):
        self._action_log.append(f"login:{username}")
        self._username = username
        self._password = password
        if username=="standard_user" and password=="secret_sauce":
            return True
        else:
            self.failed_attempts += 1
            return False
            
    @property
    def current_user(self):
        if self._username:
            return self._username
        else:
            return "anonymous"
            
    @property
    def is_authenticated(self):
        if self._username=="standard_user":
            return True
        else:
            return False
            
    @staticmethod
    def is_valid_credentials(username, password):
        return (
            isinstance(username, str)
            and isinstance(password, str)
            and bool(username)
            and bool(password)
        )
            
    def __str__(self):
        return f"LoginPage(user={self.current_user} | auth={self.is_authenticated})"

class CheckoutPage(BasePage):
    PATH = "/checkout-step-one.html"
    
    def  __init__(self, page, base_url, browser="chromium"):
        super().__init__(page, base_url, browser)
        self._first_name = None
        self._last_name = None
        self._postal_code = None
        self._order_complete = False
        
    def goto (self):
        self.navigate(CheckoutPage.PATH)
        return self
        
    def get_title(self):
        return "Checkout Page"
        
    def fill_details(self, first_name, last_name, postal_code):
        if (
            not isinstance(first_name, str) or not first_name or
            not isinstance(last_name, str) or not last_name or
            not isinstance(postal_code, str) or not postal_code
            ):
                raise ValueError("All fields required")
        
        self._first_name = first_name
        self._last_name = last_name
        self._postal_code = postal_code

        self._action_log.append(
            f"fill:{first_name}:{last_name}:{postal_code}"
        )
        return self
            
    def complete_order(self):
        if not self.is_form_complete:
            raise ValueError("Complete form first")
        else:
            self._order_complete = True
            self._action_log.append("order_complete")
            return "Order placed successfully"
            
    @property
    def is_form_complete(self):
        if self._first_name is not None and self._last_name is not None and self._postal_code is not None:
            return True
        else:
            return False
            
    @property
    def order_status(self):
        if self._order_complete:
            return "complete"
        else:
            return "pending"
            
    def __str__(self):
        return f"CheckoutPage(form={self.is_form_complete} | order={self.order_status})"
    
            
# =============================================
# DO NOT MODIFY BELOW THIS LINE
# =============================================

print("=== TESTING DAY 5 CHALLENGE ===\n")

fake_page = object()
BASE = "https://www.saucedemo.com"

# Test 1: Cannot instantiate abstract BasePage
try:
    bp = BasePage(fake_page, BASE)
    assert False, "1a - should raise TypeError"
except TypeError:
    pass
print("TEST 1 PASSED: BasePage is abstract")

# Test 2: Class attributes on BasePage
assert BasePage.DEFAULT_TIMEOUT == 30_000, "2a"
assert "chromium" in BasePage.SUPPORTED_BROWSERS, "2b"
assert "firefox" in BasePage.SUPPORTED_BROWSERS, "2c"
print("TEST 2 PASSED: BasePage class attributes")

# Test 3: BasePage.is_valid_url() static method
assert BasePage.is_valid_url("https://example.com") == True, "3a"
assert BasePage.is_valid_url("http://example.com") == True, "3b"
assert BasePage.is_valid_url("example.com") == False, "3c"
assert BasePage.is_valid_url("ftp://example.com") == False, "3d"
print("TEST 3 PASSED: BasePage.is_valid_url()")

# Test 4: BasePage.sanitise_name() static method
assert BasePage.sanitise_name("Login Test") == "login_test", "4a"
assert BasePage.sanitise_name("  CHECKOUT  ") == "checkout", "4b"
print("TEST 4 PASSED: BasePage.sanitise_name()")

# Test 5: BasePage.create() classmethod - valid browser
lp = BasePage.create.__func__(LoginPage, fake_page, BASE, "chromium")
assert isinstance(lp, LoginPage), "5a"
assert isinstance(lp, BasePage), "5b"
print("TEST 5 PASSED: BasePage.create() classmethod")

# Test 6: BasePage.create() rejects invalid browser
try:
    bad = BasePage.create.__func__(LoginPage, fake_page, BASE, "safari")
    assert False, "6a - should raise ValueError"
except ValueError:
    pass
print("TEST 6 PASSED: create() rejects invalid browser")

# Test 7: LoginPage basic creation and inheritance
lp = LoginPage(fake_page, BASE)
assert isinstance(lp, BasePage), "7a"
assert lp._loaded == False, "7b"
assert lp.failed_attempts == 0, "7c"
print("TEST 7 PASSED: LoginPage creation")

# Test 8: LoginPage.browser property (read-only)
assert lp.browser == "chromium", "8a"
try:
    lp.browser = "firefox"
    assert False, "8b - should raise AttributeError"
except AttributeError:
    pass
print("TEST 8 PASSED: browser property is read-only")

# Test 9: LoginPage.load_time_ms property with setter
assert lp.load_time_ms is None, "9a"
lp.load_time_ms = 450
assert lp.load_time_ms == 450, "9b"
try:
    lp.load_time_ms = -1
    assert False, "9c - should raise ValueError"
except ValueError:
    pass
print("TEST 9 PASSED: load_time_ms property with validation")

# Test 10: LoginPage.is_fast property
assert lp.is_fast == True, "10a"   # 450 < 1000
lp.load_time_ms = 1500
assert lp.is_fast == False, "10b"  # 1500 >= 1000
lp2 = LoginPage(fake_page, BASE)
assert lp2.is_fast == False, "10c"  # None - not loaded yet
print("TEST 10 PASSED: is_fast property")

# Test 11: LoginPage.goto() implements abstract method
lp.goto()
assert lp._loaded == True, "11a"
assert lp.is_loaded() == True, "11b"
print("TEST 11 PASSED: LoginPage.goto()")

# Test 12: LoginPage.get_title() implements abstract method
assert lp.get_title() == "Login Page", "12a"
print("TEST 12 PASSED: LoginPage.get_title()")

# Test 13: LoginPage.login() and current_user property
assert lp.current_user == "anonymous", "13a"  # not logged in yet
result = lp.login("standard_user", "secret_sauce")
assert result == True, "13b"
assert lp.current_user == "standard_user", "13c"
assert lp.is_authenticated == True, "13d"
print("TEST 13 PASSED: login() and current_user property")

# Test 14: LoginPage.login() failure
lp3 = LoginPage(fake_page, BASE)
assert lp3.login("wrong", "wrong") == False, "14a"
assert lp3.failed_attempts == 1, "14b"
assert lp3.is_authenticated == False, "14c"
assert lp3.current_user == "wrong", "14d"  # username stored even on failure
print("TEST 14 PASSED: login() failure tracking")

# Test 15: LoginPage.is_valid_credentials() static method
assert LoginPage.is_valid_credentials("user", "pass") == True, "15a"
assert LoginPage.is_valid_credentials("", "pass") == False, "15b"
assert LoginPage.is_valid_credentials("user", "") == False, "15c"
assert LoginPage.is_valid_credentials("", "") == False, "15d"
print("TEST 15 PASSED: is_valid_credentials()")

# Test 16: LoginPage __str__
s = str(lp)
assert "standard_user" in s, "16a"
assert "True" in s, "16b"
print("TEST 16 PASSED: LoginPage __str__")

# Test 17: CheckoutPage creation and inheritance
cp = CheckoutPage(fake_page, BASE)
assert isinstance(cp, BasePage), "17a"
assert cp._loaded == False, "17b"
assert cp._order_complete == False, "17c"
print("TEST 17 PASSED: CheckoutPage creation")

# Test 18: CheckoutPage abstract methods
cp.goto()
assert cp._loaded == True, "18a"
assert cp.get_title() == "Checkout Page", "18b"
print("TEST 18 PASSED: CheckoutPage abstract methods implemented")

# Test 19: CheckoutPage.is_form_complete property
assert cp.is_form_complete == False, "19a"   # note: no () - it's a property
cp.fill_details("Divya", "Kumar", "600001")
assert cp.is_form_complete == True, "19b"
assert cp._first_name == "Divya", "19c"
log = cp.get_action_log()
assert any("fill" in entry for entry in log), "19d"
print("TEST 19 PASSED: is_form_complete property and fill_details()")

# Test 20: fill_details() validates input
cp2 = CheckoutPage(fake_page, BASE)
try:
    cp2.fill_details("", "Kumar", "600001")
    assert False, "20a - should raise ValueError"
except ValueError:
    pass
try:
    cp2.fill_details("Divya", None, "600001")
    assert False, "20b - should raise ValueError"
except ValueError:
    pass
print("TEST 20 PASSED: fill_details() validates empty fields")

# Test 21: CheckoutPage.complete_order()
cp3 = CheckoutPage(fake_page, BASE)
cp3.goto()
try:
    cp3.complete_order()
    assert False, "21a - form incomplete"
except ValueError:
    pass
cp3.fill_details("Arjun", "Sharma", "400001")
msg = cp3.complete_order()
assert msg == "Order placed successfully", "21b"
assert cp3._order_complete == True, "21c"
assert cp3.order_status == "complete", "21d"
assert "order_complete" in cp3.get_action_log(), "21e"
print("TEST 21 PASSED: complete_order()")

# Test 22: order_status property
cp4 = CheckoutPage(fake_page, BASE)
assert cp4.order_status == "pending", "22a"
print("TEST 22 PASSED: order_status property")

# Test 23: CheckoutPage __str__
s = str(cp3)
assert "complete" in s, "23a"
s2 = str(cp4)
assert "pending" in s2, "23b"
print("TEST 23 PASSED: CheckoutPage __str__")

# Test 24: Polymorphism - both pages respond to same interface
def page_summary(page_obj):
    page_obj.goto()
    return {
        "title": page_obj.get_title(),
        "loaded": page_obj.is_loaded(),
        "browser": page_obj.browser,
        "fast": page_obj.is_fast
    }

lp_summary = page_summary(LoginPage(fake_page, BASE))
cp_summary = page_summary(CheckoutPage(fake_page, BASE))
assert lp_summary["title"] == "Login Page", "24a"
assert cp_summary["title"] == "Checkout Page", "24b"
assert lp_summary["loaded"] == True, "24c"
print("TEST 24 PASSED: Polymorphism with properties")

print("\nALL 24 TESTS PASSED. Day 5 complete.")