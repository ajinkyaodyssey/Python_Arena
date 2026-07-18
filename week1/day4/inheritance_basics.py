# DAY 4 - FILE 1: Inheritance and super()
# Run with: python3 inheritance_basics.py

# =============================================
# SECTION 1: What inheritance actually does
# =============================================
# Child class gets everything from parent for free.
# You only write what is DIFFERENT or NEW in the child.

print("=== BASIC INHERITANCE ===")

class BasePage:
    """Every page in the framework inherits from this."""
    
    DEFAULT_TIMEOUT = 30    # class attribute - shared by all pages
    
    def __init__(self, page, base_url):
        # Instance attributes every page needs
        self.page = page
        self.base_url = base_url
        self.loaded = False
        
    def navigate(self, path = ""):
        url = f"{self.base_url}{path}"
        print(f"Navigating to: {url}")
        self.loaded = True
        return self     # enables method chaining
        
    def get_title(self):
        return f"Page at {self.base_url}"
        
    def take_screenshot(self, name):
        print(f"Screenshot saved: {name}.png")
        
    def is_loaded(self):
        return self.loaded
        
    def __str__(self):
        return f"BasePage ({self.base_url})"
        
class LoginPage(BasePage):      #This is where inheritance happens
    """Inherits navigate, take_screenshot, is_loaded from BasePage."""

    URL_PATH = "/login"
    
    def __init__(self, page, base_url):
        super().__init__(page, base_url)    # MUST call parent __init__ first
        # Now add LoginPage-specific attributes
        self.login_attempts = 0
        self.last_error = None

    def goto(self):
        self.navigate(self.URL_PATH)        #Inherited from BasePage
        return self
    
    def login(self, username, password):
        self.login_attempts +=1
        print(f"  Filling username: {username}")
        print(f"  Filling password: {'*' * len(password)}")
        print(f"  Clicking login button")
        # Simulate success for standard_user
        return username == "standard_user" and password == "secret_sauce"
        
    def get_error_text(self):
        return self.last_error or "No Error"
        
    # Overriding parent's get_title - Overriding does not change the parent class. It only changes the behavior of the child class
    def get_title(self):
        parent_title = super().get_title()  # call parent version  #with super you reuse what the parent already does and then add your own behavior.
        return f"Login: {parent_title}"     # extend it
        
    def __str__(self):
        return f"LoginPage({self.base_url}{self.URL_PATH})"
    
    
class InventoryPage(BasePage):
    """Also inherits from BasePage."""
    
    URL_PATH = "/inventory.html"
    
    def __init__(self, page, base_url):
        super().__init__(page, base_url)
        self.cart_count = 0
        self._items = []
        
    def goto(self):
        self.navigate(self.URL_PATH)
        return self
        
    def add_to_cart(self, item_name):
        self._items.append(item_name)
        self.cart_count+=1
        print(f"  Added to cart: {item_name} (cart: {self.cart_count})")
        return self
    
    def get_cart_count(self):
        return self.cart_count
        
    def get_title(self):
        return f"Inventory: {super().get_title()}"
        
    def __str__(self):
        return f"InventoryPage({self.base_url}{self.URL_PATH})"