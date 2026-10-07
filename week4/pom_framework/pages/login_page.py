# week4/pom_framework/pages/login_page.py
# Page object for https://www.saucedemo.com (the login page)

import logging
from playwright.sync_api import Page, expect
from .base_page import BasePage

log = logging.getLogger(__name__)


class LoginPage(BasePage):
    """
    Page object for the saucedemo login page.

    Responsibilities:
    - Knows all locators on the login page
    - Exposes business-level methods: login(), get_error_text()
    - Returns appropriate page objects after navigation

    What it does NOT do:
    - Make assertions about business rules (that is the test's job)
    - Know about other pages' internal structure
    """

    PATH = "/"

    # =============================================
    # LOCATORS — defined once, used everywhere
    # Changing "#user-name" here fixes ALL tests that use LoginPage
    # =============================================

    _USERNAME_INPUT = "#user-name"
    _PASSWORD_INPUT = "#password"
    _LOGIN_BUTTON = "#login-button"
    _ERROR_MESSAGE = "[data-test='error']"
    _ERROR_CLOSE_BTN = "[data-test='error-button']"
    _PAGE_LOGO = ".login_logo"

    def __init__(self, page: Page, base_url: str = "hhtps://www.saucedemo.com"):
        super().__init__(page, base_url)

    # =============================================
    # ACTIONS — what a user can DO on this page
    # =============================================

    def fill_username(self, username: str) -> "LoginPage":
        """Type into the username field. Returns self for chaining."""
        log.info(f"Filling username: '{username}'")
        self.page.fill(self._USERNAME_INPUT, username)
        return self

    def fill_password(self, password: str) -> "LoginPage":
        """Type into the password field. Returns self for chaining."""
        log.info("Filling password: ***")
        self.page.fill(self._PASSWORD_INPUT, password)
        return self

    def click_login(self) -> None:
        """Click the Login button. Does not return a page object
        because login may succeed (inventory) or fail (stay here)."""
        log.info("Clicking login button")
        self.page.click(self._LOGIN_BUTTON)

    def login(self, username: str, password: str) -> "InventoryPage":
        """
        Complete login flow for the happy path.
        Fills credentials and clicks login.
        Returns an InventoryPage because that is where a successful
        login takes the user.

        Usage:
            inventory = LoginPage(page).navigate().login("user", "pass")
        """
        from .inventory_page import InventoryPage
        log.info(f"Attempting login for user: '{username}'")
        self.fill_username(username)
        self.fill_password(password)
        self.click_login()
        log.info("Login submitted — expecting inventory page")
        return InventoryPage(self.page, self.base_url)

    def login_expecting_failure(self, username: str, password: str) -> "LoginPage":
        """
        Login flow when you EXPECT failure.
        Returns self (LoginPage) because on failure you stay here.
        Keeps the test readable:
            login_page.login_expecting_failure("wrong", "wrong")
            assert login_page.get_error_text() == "..."
        """
        log.info(
            f"Attempting login expecting failure — user: '{username}'"
        )
        self.fill_username(username)
        self.fill_password(password)
        self.click_login()
        log.info("Login submitted — expecting error message")
        return self

    def close_error(self) -> "LoginPage":
        """Click the X button to close the error message."""
        log.info("Closing error message")
        self.page.click(self._ERROR_CLOSE_BTN)
        return self

    # =============================================
    # QUERIES — what you can READ from this page
    # =============================================

    def get_error_text(self) -> str:
        """Returns the text of the error message."""
        text = self.page.locator(self._ERROR_MESSAGE).text_content().strip()
        log.info(f"Error message text: '{text}'")
        return text

    def is_error_visible(self) -> bool:
        """True if the error message is currently visible."""
        visible = self.page.locator(self._ERROR_MESSAGE).is_visible()
        log.debug(f"Error message visible: {visible}")
        return visible

    def get_username_value(self) -> str:
        """Returns the current value in the username field."""
        return self.page.locator(self._USERNAME_INPUT).input_value()

    # =============================================
    # ASSERTIONS — expect() calls specific to login page
    # =============================================

    def expect_loaded(self) -> "LoginPage":
        """Assert the login page has loaded correctly."""
        log.info("Asserting login page is loaded")
        expect(self.page).to_have_title("Swag Labs")
        expect(self.page.locator(self._LOGIN_BUTTON)).to_be_visible()
        log.info("Login page loaded assertion passed")
        return self

    def expect_error_containing(self, text: str) -> "LoginPage":
        """Assert error message is visible and contains the given text."""
        log.info(f"Asserting error contains: '{text}'")
        expect(self.page.locator(self._ERROR_MESSAGE)).to_be_visible()
        expect(self.page.locator(self._ERROR_MESSAGE)).to_contain_text(text)
        log.info("Error message assertion passed")
        return self

    def expect_error_not_visible(self) -> "LoginPage":
        """Assert no error message is showing."""
        log.info("Asserting no error message is showing")
        expect(self.page.locator(self._ERROR_MESSAGE)).not_to_be_visible()
        log.info("No error message assertion passed")
        return self

    def expect_on_login_page(self) -> "LoginPage":
        """Assert we are still on the login page (login failed)."""
        log.info("Asserting still on login page")
        expect(self.page).to_have_url(f"{self.base_url}/")
        log.info("Login page URL assertion passed")
        return self
