# DAY 4 - FILE 3: Challenge
# Build BasePage, LoginPage, CheckoutPage from scratch
# Run with: python3 day4_challenge.py

# INSTRUCTIONS:
#
# CLASS 1: BasePage
#   Class attribute:
#     - DEFAULT_TIMEOUT = 30_000
#   __init__(self, page, base_url):
#     - self.page = page
#     - self.base_url = base_url
#     - self._loaded = False
#     - self._action_log = []   (list of strings tracking actions)
#   Methods:
#     - navigate(path="")
#         logs f"navigate:{self.base_url}{path}" to _action_log
#         sets _loaded = True
#         returns self
#     - get_title()
#         returns f"Page({self.base_url})"
#     - is_loaded()
#         returns self._loaded
#     - get_action_log()
#         returns self._action_log
#     - take_screenshot(name)
#         logs f"screenshot:{name}" to _action_log
#         returns f"{name}.png"
#     - __str__
#         returns f"BasePage(url={self.base_url})"
#
# CLASS 2: LoginPage(BasePage)
#   Class attribute:
#     - PATH = "/login"
#   __init__(self, page, base_url):
#     - call super().__init__()
#     - self.is_authenticated = False
#     - self.failed_attempts = 0
#   Methods:
#     - goto()
#         calls self.navigate(self.PATH)
#         returns self
#     - login(username, password)
#         logs f"login:{username}" to _action_log
#         if username=="standard_user" and password=="secret_sauce":
#             sets self.is_authenticated = True
#             returns True
#         else:
#             increments self.failed_attempts
#             returns False
#     - get_failed_attempts()
#         returns self.failed_attempts
#     - get_title()     <- OVERRIDE parent
#         returns f"Login | {super().get_title()}"
#     - __str__
#         auth = "authenticated" if self.is_authenticated else "not authenticated"
#         returns f"LoginPage({self.base_url} | {auth})"
#
# CLASS 3: CheckoutPage(BasePage)
#   Class attribute:
#     - PATH = "/checkout-step-one.html"
#   __init__(self, page, base_url):
#     - call super().__init__()
#     - self.first_name = None
#     - self.last_name = None
#     - self.postal_code = None
#     - self._order_complete = False
#   Methods:
#     - goto()
#         calls self.navigate(self.PATH)
#         returns self
#     - fill_details(first_name, last_name, postal_code)
#         sets self.first_name, self.last_name, self.postal_code
#         logs f"fill_details:{first_name}:{last_name}:{postal_code}"
#         returns self
#     - is_form_complete()
#         returns True if first_name, last_name, postal_code are all not None
#         returns False otherwise
#     - complete_order()
#         if not is_form_complete(): raise ValueError("Form incomplete")
#         sets self._order_complete = True
#         logs "complete_order"
#         returns "Order completed successfully"
#     - get_title()     <- OVERRIDE parent
#         returns f"Checkout | {super().get_title()}"
#     - __str__
#         status = "complete" if self._order_complete else "in progress"
#         returns f"CheckoutPage({self.base_url} | {status})"


class BasePage:
    DEFAULT_TIMEOUT = 30_000
    
    def __init__(self, page, base_url):
        self.page = page
        self.base_url = base_url
        self._loaded = False
        self._action_log = []
    
    def navigate(self, path = ""):
        self._action_log.append(f"navigate:{self.base_url}{path}")
        self._loaded = True
        return self
    
    def get_title(self):
        return f"Page({self.base_url})"
        
    def is_loaded(self):
        return self._loaded
    
    def get_action_log(self):
        return self._action_log
    
    def take_screenshot(self, name):
        self._action_log.append(f"screenshot:{name}")
        return  f"{name}.png"

    def __str__(self):
        return f"BasePage(url={self.base_url})"

    
    
class LoginPage(BasePage):
    PATH = "/login"
    
    def __init__(self, page, base_url):
        super().__init__(page, base_url)
        self.is_authenticated = False
        self.failed_attempts = 0
    
    def goto(self):
        self.navigate(self.PATH)
        return self
        
    def login(self, username, password):
        self._action_log.append(f"login:{username}")
        if username == "standard_user" and password =="secret_sauce":
            self.is_authenticated = True
            return True
        else:
            self.failed_attempts+=1
            return False
            
    def get_failed_attempts(self):
        return self.failed_attempts
        
    def get_title(self):
        return  f"Login | {super().get_title()}"
        
    def __str__(self):
        auth = "authenticated" if self.is_authenticated else "not authenticated"
        return f"LoginPage({self.base_url} | {auth})"

class CheckoutPage(BasePage):
    PATH = "/checkout-step-one.html"
    def __init__(self, page, base_url):
        super().__init__(page, base_url)
        self.first_name = None
        self.last_name = None
        self.postal_code = None
        self._order_complete = False
        
    def goto(self):
        self.navigate(self.PATH)
        return self
    
    def fill_details(self, first_name, last_name, postal_code):
        self.first_name = first_name        # actually SET the attributes
        self.last_name = last_name
        self.postal_code = postal_code
        self._action_log.append(           # actually LOG it
        f"fill_details:{first_name}:{last_name}:{postal_code}")
        return self
    
    def is_form_complete(self):
        if self.first_name != None and self.last_name != None and self.postal_code!= None:
            return True
        else:
            return False
            
    def complete_order(self):
        if not self.is_form_complete():
            raise ValueError("Form incomplete")
        self._order_complete = True
        self._action_log.append("complete_order")   # LOG it, don't print it
        return "Order completed successfully"
            
    def get_title(self):
        return f"Checkout | {super().get_title()}"

    def __str__(self):
        if self._order_complete:
            status = "complete"
        else:
            status = "in progress"
        
        return f"CheckoutPage({self.base_url} | {status})"

# =============================================
# DO NOT MODIFY BELOW THIS LINE
# =============================================

print("=== TESTING PAGE CLASSES ===\n")

fake_page = object()
BASE = "https://www.saucedemo.com"

# Test 1: BasePage class attribute
assert BasePage.DEFAULT_TIMEOUT == 30_000, "1a"
print("TEST 1 PASSED: BasePage.DEFAULT_TIMEOUT")

# Test 2: BasePage __init__
bp = BasePage(fake_page, BASE)
assert bp.page is fake_page, "2a"
assert bp.base_url == BASE, "2b"
assert bp._loaded == False, "2c"
assert bp._action_log == [], "2d"
print("TEST 2 PASSED: BasePage __init__")

# Test 3: BasePage navigate()
result = bp.navigate("/inventory.html")
assert bp._loaded == True, "3a"
assert result is bp, "3b"  # returns self
assert "navigate:https://www.saucedemo.com/inventory.html" in bp._action_log, "3c"
print("TEST 3 PASSED: BasePage navigate()")

# Test 4: BasePage methods
assert bp.is_loaded() == True, "4a"
assert bp.get_title() == "Page(https://www.saucedemo.com)", "4b"
screenshot = bp.take_screenshot("test_shot")
assert screenshot == "test_shot.png", "4c"
assert "screenshot:test_shot" in bp.get_action_log(), "4d"
print("TEST 4 PASSED: BasePage methods")

# Test 5: BasePage __str__
assert str(bp) == "BasePage(url=https://www.saucedemo.com)", "5a"
print("TEST 5 PASSED: BasePage __str__")

# Test 6: LoginPage inherits from BasePage
lp = LoginPage(fake_page, BASE)
assert isinstance(lp, LoginPage), "6a"
assert isinstance(lp, BasePage), "6b"  # IS ALSO a BasePage
assert lp._loaded == False, "6c"       # inherited attribute
assert lp.is_authenticated == False, "6d"
assert lp.failed_attempts == 0, "6e"
print("TEST 6 PASSED: LoginPage inheritance and __init__")

# Test 7: LoginPage.goto() uses inherited navigate()
lp.goto()
assert lp._loaded == True, "7a"        # set by inherited navigate()
assert lp.is_loaded() == True, "7b"   # inherited method
print("TEST 7 PASSED: LoginPage.goto()")

# Test 8: LoginPage.login() success
result = lp.login("standard_user", "secret_sauce")
assert result == True, "8a"
assert lp.is_authenticated == True, "8b"
assert lp.failed_attempts == 0, "8c"
assert "login:standard_user" in lp.get_action_log(), "8d"
print("TEST 8 PASSED: LoginPage.login() success")

# Test 9: LoginPage.login() failure
lp2 = LoginPage(fake_page, BASE)
result2 = lp2.login("wrong_user", "wrong_pass")
assert result2 == False, "9a"
assert lp2.is_authenticated == False, "9b"
assert lp2.failed_attempts == 1, "9c"
lp2.login("another_wrong", "pass")
assert lp2.failed_attempts == 2, "9d"
print("TEST 9 PASSED: LoginPage.login() failure")

# Test 10: LoginPage.get_title() overrides BasePage.get_title()
title = lp.get_title()
assert title == "Login | Page(https://www.saucedemo.com)", "10a"
assert "Login" in title, "10b"
print("TEST 10 PASSED: LoginPage.get_title() override")

# Test 11: LoginPage __str__
assert "authenticated" in str(lp), "11a"
lp3 = LoginPage(fake_page, BASE)
assert "not authenticated" in str(lp3), "11b"
print("TEST 11 PASSED: LoginPage __str__")

# Test 12: CheckoutPage inherits from BasePage
cp = CheckoutPage(fake_page, BASE)
assert isinstance(cp, CheckoutPage), "12a"
assert isinstance(cp, BasePage), "12b"
assert cp._loaded == False, "12c"
assert cp.first_name is None, "12d"
assert cp._order_complete == False, "12e"
print("TEST 12 PASSED: CheckoutPage inheritance and __init__")

# Test 13: CheckoutPage.goto()
cp.goto()
assert cp._loaded == True, "13a"
print("TEST 13 PASSED: CheckoutPage.goto()")

# Test 14: CheckoutPage.fill_details() and is_form_complete()
assert cp.is_form_complete() == False, "14a"  # nothing filled yet
result = cp.fill_details("Divya", "Kumar", "600001")
assert result is cp, "14b"                     # returns self
assert cp.first_name == "Divya", "14c"
assert cp.last_name == "Kumar", "14d"
assert cp.postal_code == "600001", "14e"
assert cp.is_form_complete() == True, "14f"
log = cp.get_action_log()
assert any("fill_details" in entry for entry in log), "14g"
print("TEST 14 PASSED: fill_details() and is_form_complete()")

# Test 15: CheckoutPage.complete_order()
cp2 = CheckoutPage(fake_page, BASE)
cp2.goto()
try:
    cp2.complete_order()   # form not filled yet
    assert False, "15a - should have raised ValueError"
except ValueError:
    pass

cp2.fill_details("Arjun", "Sharma", "400001")
msg = cp2.complete_order()
assert msg == "Order completed successfully", "15b"
assert cp2._order_complete == True, "15c"
assert "complete_order" in cp2.get_action_log(), "15d"
print("TEST 15 PASSED: CheckoutPage.complete_order()")

# Test 16: CheckoutPage.get_title() override
title = cp.get_title()
assert title == "Checkout | Page(https://www.saucedemo.com)", "16a"
print("TEST 16 PASSED: CheckoutPage.get_title() override")

# Test 17: CheckoutPage __str__
assert "in progress" in str(cp2) or "complete" in str(cp2), "17a"
cp3 = CheckoutPage(fake_page, BASE)
assert "in progress" in str(cp3), "17b"
print("TEST 17 PASSED: CheckoutPage __str__")

# Test 18: Polymorphism - all pages work with same function
def describe_page(page_obj):
    return f"{page_obj.get_title()} | loaded={page_obj.is_loaded()}"

descriptions = [describe_page(p) for p in [bp, lp, cp]]
assert "Login" in descriptions[1], "18a"
assert "Checkout" in descriptions[2], "18b"
print("TEST 18 PASSED: Polymorphism")

# Test 19: DEFAULT_TIMEOUT accessible on all subclasses
assert LoginPage.DEFAULT_TIMEOUT == 30_000, "19a"
assert CheckoutPage.DEFAULT_TIMEOUT == 30_000, "19b"
assert lp.DEFAULT_TIMEOUT == 30_000, "19c"
print("TEST 19 PASSED: Inherited class attribute")

print("\nALL 19 TESTS PASSED. Day 4 complete.")