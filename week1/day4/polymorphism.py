# DAY 4 - FILE 2: Polymorphism and Abstract Classes
# Run with: python3 polymorphism.py

from abc import ABC, abstractmethod


# =============================================
# SECTION 1: Polymorphism
# =============================================
#Different classes can be used interchangeably
#If they share the same interface (method name)
#The function dosent care WHICH class it gets, only that it has the method it needs


print("=== POLYMORPHISM ===")

class BasePage:
    def __init__(self, page, base_url):
        self.page = page
        self.base_url = base_url
        
    def get_title(self):
        raise NotImplementedError("Subclass must implement get_title()")
        
    def navigate(self, path = ""):
        print(f" -> {self.base_url}{path}")
        return self
    
class LoginPage(BasePage):
    def get_title(self):
        return "Login Page"
        
    def login(self, username, password):
        print(f" Logging in as {username}")
        
class InventoryPage(BasePage):
    def get_title(self):
        return "Products Page"
        
    def add_to_cart(self, item):
        print(f"Adding {item} to cart")
        
class CheckoutPage(BasePage):
    def get_title(self):
        return "Checkout Page"
        
    def complete_order(self):
        print(" Order completed")
        
        
#Polymorphism in action:
#This function works with ANY BasePage subclass

def print_page_info(page_object):       #this function isnt inside class thats why no self
    print(f"Page title: {page_object.get_title()}")
    print(f"Base URL: {page_object.base_url}")
    
fake_page = object()        #plain, empty Python object     #object is Python's most basic built-in class
pages = [
    LoginPage(fake_page, "https://saucedemo.com"),
    InventoryPage(fake_page, "https://saucedemo.com"),
    CheckoutPage(fake_page, "https://saucedemo.com"),
]

for page in pages:
    print_page_info(page)   # same function, different class each time
    print()     #only for one line gap
    
        
# =============================================
# SECTION 2: Abstract Base Classes
# =============================================


#ABC enforces that subclasses MUST implement certain methods.
#If they dont, python raises TypeError at instantiation
#This catches missing implementations immediately

print("=== ABSTRACT BASE CLASSES ===")      #Abstract Base Class (ABC).

class BaseReporter(ABC):        #Abstract Base Class (ABC)
    
    @abstractmethod
    def generate(self, results):
        """Every reporter MUST implement this."""
        pass

    @abstractmethod
    def save(self, filepath):
        """Every reporter MUST implement this."""
        pass
    
    # Concrete method - subclasses get this for free, no override needed
    def summarize (self, results):
        passed = sum(1 for r in results if r ["status"] == "PASS")
        failed = len(results) - passed
        return {
            "total": len(results),
            "passed": passed,
            "failed": failed,
            "pass_rate": round(passed / len(results) * 100, 1) if results else 0
        }
        
class HTMLReporter(BaseReporter):
    def generate(self, results):
        summary = self.summarise(results)   # inherited concrete method
        rows = ""
        for r in results:
            color = "green" if r["status"] == "PASS" else "red"
            rows += f'<tr><td>{r["name"]}</td><td style="color:{color}">{r["status"]}</td></tr>'
        return f"""
        <html><body>
        <h1>Test Report</h1>
        <p>Total: {summary['total']} | Passed: {summary['passed']} | Failed: {summary['failed']}</p>
        <table border="1">{rows}</table>
        </body></html>
        """

    def save(self, filepath):
        print(f"  Saving HTML report to: {filepath}")


class JSONReporter(BaseReporter):
    def generate(self, results):
        import json
        return json.dumps({
            "summary": self.summarise(results),
            "results": results
        }, indent=2)

    def save(self, filepath):
        print(f"  Saving JSON report to: {filepath}")


# Cannot instantiate abstract class
try:
    r = BaseReporter()
except TypeError as e:
    print(f"Cannot instantiate ABC: {e}")

# Can instantiate concrete subclasses
html_reporter = HTMLReporter()
json_reporter = JSONReporter()

results = [
    {"name": "login_test", "status": "PASS"},
    {"name": "checkout_test", "status": "FAIL"},
    {"name": "search_test", "status": "PASS"},
]

# Polymorphism - same interface, different output
for reporter in [html_reporter, json_reporter]:
    output = reporter.generate(results)     # same method name, different result
    reporter.save("reports/output")
    summary = reporter.summarize(results)   # inherited, same for both
    print(f"{reporter.__class__.__name__}: {summary}")


# =============================================
# SECTION 3: Method Resolution Order (MRO)
# =============================================
# When Python looks up a method, it follows the MRO.
# For single inheritance: Child -> Parent -> object
# This is the order Python searches for the method.


print("\n=== METHOD RESOLUTION ORDER ===")

class A:
    def hello(self):
        return "Hello from A"

class B(A):
    def hello(self):
        return "Hello from B"

class C(B):
    pass    # no hello() defined here

c = C()
print(c.hello())    # "Hello from B" -- C has no hello, goes up to B, finds it

print(C.__mro__)    # (<class 'C'>, <class 'B'>, <class 'A'>, <class 'object'>)
# Python searches left to right - C first, then B, then A, then object

class D(B):
    def hello(self):
        result = super().hello()    # super() follows MRO - calls B.hello()
        return f"D extending: {result}"

d = D()
print(d.hello())    # "D extending: Hello from B"