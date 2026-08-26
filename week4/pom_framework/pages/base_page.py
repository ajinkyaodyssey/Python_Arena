# week4/pom_framework/pages/base_page.py
# Foundation class for all page objects.
# Every page class inherits from this.
# Contains shared behaviour — navigation, screenshots, title.

import os
import logging
from playwright.sync_api import Page, expect

log = logging.getLogger(__name__)       #Create/get a logger whose name is the current Python module’s name.


class BasePage:
    """
    Base class for all page objects in this framework.

    Design principles:
    - Every page class inherits from BasePage
    - BasePage never knows about specific page content
    - It only knows about things EVERY page has: URL, title, screenshot
    - Child classes add page-specific locators and methods
    """
    
    # Subclasses override this with their specific URL path
    # Example: LoginPage sets PATH = "/"
    #          InventoryPage sets PATH = "/inventory.html" 
    PATH: str = ""
    
    def __init__(self, page: Page, base_url: str = "https::/www.saucedemo.com"):
        self.page = page
        self.base_url = base_url
        self._url = f"{base_url}{self.PATH}"     # Because PATH belongs to the class, but self.PATH lets each subclass/instance provide its own value
    
    
    # =============================================
    # NAVIGATION
    # =============================================
    
    def navigate(self) -> "BasePage":
        """
        Navigate to this page's URL.
        Returns self to enable method chaining:
            login_page = LoginPage(page).navigate()
        """
        log.info(f"Navigating to {self._url}")
        self.page.goto(self._url)       # My Login Page Object → give me the browser tab → navigate it
        log.info(f"Navigation complete. Current URL: {self.page.url}")
        return self
        
    def get_title(self) -> str:
        title = self.page.title()
        log.debug(f"Page title: {title}")
        return title
        
    def get_url(self) -> str:
        """Returns the current browser URL"""
        return self.page.url()
        
    
    # =============================================
    # WAITING
    # =============================================
    
    def wait_for_url(self, expected_url: str) -> "BasePage":
        """Wait until browser URL matches the expected_url"""
        log.info(f"Waiting for URL: {expected_url}")
        self.page.wait_for_url(expected_url)
        return self         #After I'm done waiting, give the same BasePage object back
        
    def wait_for_load_state(self, state: str = "load") -> "BasePage":
        log.info(f"Waiting for load state: {state}")
        self.page.wait_for_load_state(state)
        return self
        
    
    # =============================================
    # SCREENSHOTS AND DEBUGGING
    # =============================================
    
    def take_screenshot(self, name: str) -> str:
        """
        Take a screenshot and save it.
        Returns the path so tests can log it.
        Used automatically by the failure screenshot hook in conftest.
        """
        import os
        os.makedirs("reports/screenshots", exist_ok=True)   # Create folder if it doesn't exist
            # os.makedirs(path, exist_ok=True) creates the required folder(s).
            # exist_ok=True means don't throw an error if the folder already exists.
            # Remember:
            # makedirs = make directories
            # exist_ok=True = already exists? No problem.
        path = f"reports/screenshots/{name}.png"
        self.page.screenshot(path = path)       # Take a screenshot of the current browser page and save it at the location stored in path
        log.info(f"Screenshot saved: {path}")
        return path
        
    def take_full_page_screenshot(self, name: str) -> str:
        """Full page screenshot — captures content below the fold."""
        os.makedirs("reports/screenshots", exist_ok=True)
        path = f"reports/screenshots/{name}_full.png"
        self.page.screenshot(path=path, full_page=True)
        log.info(f"Full page screenshot saved: {path}")
        return path
        
    
    # =============================================
    # COMMON ASSERTIONS
    # =============================================
    
    def expect_url(self, expected_url: str) -> "BasePage":
        """Assert current URL matches expected."""
        log.info(f"Asserting URL is: {expected_url}")
        expect(self.page).to_have_url(expected_url)
        log.info("URL assertion passed")
        return self
        
    def expect_title(self, expected_title: str) -> "BasePage":
        """Assert browser tab matches expected."""
        log.info(f"Asserting title is: {expected_title}")
        expect(self.page).to_have_title(expected_title)
        log.info("Title assertion passed")
        return self
        
    
    # =============================================
    # DUNDER METHODS
    # =============================================
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(url={self.page.url})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(base_url={self.base_url!r})"
        
    

# =============================================================
# REVISION NOTES — BASE PAGE / POM
# =============================================================
#
# 1. self
#    self = the current object.
#
#    self.page   -> this object's Playwright Page
#    self.PATH   -> this object's PATH
#    self._url   -> this object's URL
#
#
# 2. self.PATH
#    Allows each child class to define its own URL.
#
#    class LoginPage(BasePage):
#        PATH = "/"
#
#    class InventoryPage(BasePage):
#        PATH = "/inventory.html"
#
#    self.PATH automatically uses the PATH of the actual
#    child object.
#
#
# 3. Page Object vs Playwright Page
#
#    LoginPage      -> our Python Page Object
#    self.page      -> actual Playwright browser Page
#
#    self.page.goto(self._url)
#    -> Use the Playwright browser page to navigate to this
#       Page Object's URL.
#
#
# 4. return self
#    Returns the SAME object after the method finishes.
#    This allows method chaining.
#
#    Example:
#    login_page.navigate().wait_for_url(url).expect_title(title)
#
#
# 5. os.makedirs()
#
#    os.makedirs("reports/screenshots", exist_ok=True)
#
#    -> Creates the required folder(s).
#    -> exist_ok=True means don't throw an error if the
#       folder already exists.
#
#    Remember:
#    makedirs     = make directories
#    exist_ok=True = already exists? No problem.
#
#
# 6. Screenshot
#
#    self.page.screenshot(path=path)
#
#    -> Takes a screenshot of the current browser page
#       and saves it to the given path.
#
#    full_page=True
#    -> Captures the entire page, including content below
#       the visible screen.
#
#
# 7. Type Hints
#
#    page: Page
#    name: str
#    expected_url: str
#    -> BasePage
#    -> str
#
#    -> Tell the reader/tools what type of value is expected
#       or returned.
#
#
# 8. Inheritance
#
#    class LoginPage(BasePage):
#
#    -> LoginPage inherits common functionality from BasePage.
#    -> LoginPage can then add its own locators and methods.
#
#    BasePage     = common functionality
#    Child Page   = page-specific functionality
#
#
# 9. _url
#
#    self._url
#
#    -> "_" means this attribute is intended for internal use.
#    -> Python does NOT strictly make it private.
#
#
# 10. Playwright expect()
#
#    expect(self.page).to_have_url(expected_url)
#    expect(self.page).to_have_title(expected_title)
#
#    -> Used to verify that the browser is in the expected state.
#
#
# 11. __str__ and __repr__
#
#    These are special/dunder methods.
#
#    __str__  -> user-friendly representation of the object
#    __repr__ -> developer/debug representation of the object
#
#
# 12. self.__class__.__name__
#
#    -> Gets the actual class name of the current object.
#
#    Example:
#    LoginPage
#    InventoryPage
#    CheckoutPage
#
#
# =============================================================
# MOST IMPORTANT FOR SDET REVISION
# =============================================================
#
# self             -> current object
# self.page        -> actual Playwright browser page
# self.PATH        -> child-specific PATH
# self._url        -> current Page Object's URL
# return self      -> enables method chaining
# inheritance      -> reuse common page behavior
# POM              -> separates common and page-specific logic
# expect()         -> assertions / verification
# screenshot()     -> debugging / test evidence
#
# =============================================================