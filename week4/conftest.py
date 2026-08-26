# week4/pom_framework/tests/conftest.py
# Production-grade conftest for the POM framework.
#
# FIXTURE SCOPES — why each is what it is:
#
# browser       = session  | One launch per run. Expensive. Shared safely.
# page          = function | Fresh context per test. Isolation guaranteed.
# auth_storage = session   | Login once. Save JSON. Reuse everywhere.
# logged_in_page = function | Fresh context + auth state. Fast + isolated.
#
# RULE: expensive shared resources = session scope
#        per-test isolation = function scope

import pytest                                           # Testing framework core
import os                                               # File and directory utilities
import logging                                          # Standard Python logging library
from playwright.sync_api import (                      # Synchronous Playwright API imports
    Page,                                               # Type hint for browser tab/page
    Browser,                                            # Type hint for browser process
    BrowserContext,                                     # Type hint for browser profile/session
)

from week4.pom_framework.pages.login_page import LoginPage        # Imports Login Page Object class
from week4.pom_framework.pages.inventory_page import InventoryPage  # Imports Inventory Page Object class
from week4.pom_framework.pages.cart_page import CartPage            # Imports Cart Page Object class
from week4.pom_framework.pages.checkout_page import CheckoutPage    # Imports Checkout Page Object class

# =============================================
# CONFIGURATION
# =============================================

BASE_URL = "https://www.saucedemo.com"                  # Target application URL
VALID_USER = "standard_user"                            # Default login username
VALID_PASS = "secret_sauce"                             # Default login password
AUTH_STATE_PATH = "/tmp/pom_suite_auth.json"           # Path to store saved login session
SCREENSHOT_DIR = "reports/screenshots"                  # Directory path for failure screenshots

logging.basicConfig(                                    # Configures global log output formatting
    level=logging.INFO,                                 # Sets minimum log level to INFO
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s" # Sets log message layout format
)


# =============================================
# FIXTURE 1: browser — SESSION SCOPE
# =============================================

# @pytest.fixture(scope="session")                        # Runs once for the entire test session
# def playwright_instance() -> Playwright:                # Starts and manages the Playwright engine
#     """
#     Start and stop the Playwright process once per session.
#     The `with sync_playwright()` block must stay open for the
#     entire session — if it closes, all browsers close with it.
#     """
#     with sync_playwright() as pw:                      # Context manager starting Playwright driver
#         yield pw                                        # Provides engine instance; cleans up after session


@pytest.fixture(scope="session")                        # Runs once for the entire test session
def browser(playwright) -> Browser:                     # Uses pytest-playwright's built-in playwright fixture
    """
    Launch ONE browser for the entire test session.
    Uses pytest-playwright's built-in 'playwright' fixture
    instead of sync_playwright() to avoid asyncio conflict.

    Why session scope:
    - Browser launch takes 1-2 seconds
    - 40 tests * 2s = 80 seconds wasted if function-scoped
    - The browser itself is stateless between tests
      (state lives in contexts, not the browser)

    headless=True because:
    - Codespaces has no display server
    - CI pipelines have no display server
    - Headless is the production-correct way to run
    """
    browser = playwright.chromium.launch(headless=True) # Launches headless Chromium browser
    yield browser                                       # Provides browser to downstream fixtures
    browser.close()                                     # Terminates browser process when session ends                                 # Terminates browser process when session ends


# =============================================
# FIXTURE 2: page — FUNCTION SCOPE
# =============================================

@pytest.fixture(scope="function")                       # Runs once per test function for isolation
def context(browser: Browser) -> BrowserContext:        # Creates clean browser context (Incognito)
    """
    Fresh browser context per test.
    A context is like a browser profile — isolated cookies,
    localStorage, sessionStorage.
    Closing it after each test wipes all state completely.
    """
    ctx = browser.new_context(                         # Initializes clean browser session context
        viewport={"width": 1280, "height": 720},        # Configures browser resolution
        ignore_https_errors=True,                       # Ignores SSL certificate errors
    )
    ctx.set_default_timeout(20_000)                     # Sets global 20-second action timeout
    yield ctx                                           # Provides context to test or dependent fixtures
    ctx.close()                                         # Closes context & wipes storage after test completes


@pytest.fixture(scope="function")                       # Runs once per test function
def page(context: BrowserContext) -> Page:             # Creates clean browser tab
    """
    Fresh page per test, inside the fresh context.
    Function scope = complete test isolation.
    Test 1 cannot affect Test 2 through shared page state.
    """
    pg = context.new_page()                             # Opens new tab in current context
    yield pg                                            # Yields tab instance to the test function
    # No need to close — context.close() handles it


# =============================================
# FIXTURE 3: auth_storage — SESSION SCOPE
# =============================================

@pytest.fixture(scope="session")                        # Runs once across whole test suite
def auth_storage(browser: Browser) -> str:             # Handles logging in and caching auth state
    """
    Log in ONCE per session. Save full browser state to JSON.
    Return the path — other fixtures load from it.

    What the JSON contains:
    - cookies: session token the server uses to identify logged-in user
    - origins: localStorage and sessionStorage data

    Why session scope:
    - Login takes 2-3 seconds per call
    - 30 authenticated tests * 2.5s = 75 seconds saved
    - The saved state is read-only — safe to share across tests
      because each test gets its own COPY via new_context(storage_state=)

    The file is only created if it doesn't exist yet.
    On a fresh run it creates it. On re-runs it reuses it.
    Delete the file to force a fresh login on next run.
    """
    if not os.path.exists(AUTH_STATE_PATH):             # Checks if session JSON file is missing
        logging.info("Auth state not found. Logging in to create it.") # Logs initial state setup message
        ctx = browser.new_context(                      # Creates temporary context for login setup
            viewport={"width": 1280, "height": 720}     # Sets screen dimensions
        )
        pg = ctx.new_page()                             # Opens new tab for authentication
        pg.set_default_timeout(20_000)                  # Sets action timeout to 20 seconds

        # Use LoginPage to authenticate — consistent with the framework
        LoginPage(pg, BASE_URL).navigate().login(VALID_USER, VALID_PASS) # Executes login UI sequence
        pg.wait_for_url(f"{BASE_URL}/inventory.html")   # Waits until user reaches inventory page

        # Save the entire browser state
        ctx.storage_state(path=AUTH_STATE_PATH)         # Exports cookies & state to JSON file
        logging.info(f"Auth state saved to {AUTH_STATE_PATH}") # Logs successful auth export
        ctx.close()                                     # Closes temporary context
    else:
        logging.info(f"Reusing auth state from {AUTH_STATE_PATH}") # Logs reuse of existing session file

    return AUTH_STATE_PATH                              # Returns file path string to caller fixtures


# =============================================
# FIXTURE 4: logged_in_page — FUNCTION SCOPE
# =============================================

@pytest.fixture(scope="function")                       # Runs per test requiring pre-authenticated session
def logged_in_page(browser: Browser, auth_storage: str) -> Page: # Yields pre-logged-in browser page
    """
    The core authenticated fixture.
    Creates a NEW context loaded with saved auth state.
    Starts on the inventory page, already logged in.

    Why this design:
    - new_context(storage_state=path) copies the saved cookies/storage
      into the new context — not a shared reference. Each test gets
      its own independent copy. Test 1 adding items to cart does not
      affect Test 2's cart.
    - Function scope ensures cleanup after every test.
    - No login flow = no network round-trip = fast test setup.

    Usage in tests:
        def test_something(logged_in_page: Page):
            inventory = InventoryPage(logged_in_page, BASE_URL)
            inventory.expect_loaded()
    """
    ctx = browser.new_context(                         # Initializes fresh isolated context...
        storage_state=auth_storage,                     # ...preloaded with saved login cookies
        viewport={"width": 1280, "height": 720},        # Sets viewport resolution
        ignore_https_errors=True,                       # Bypasses HTTPS errors
    )
    ctx.set_default_timeout(20_000)                     # Sets global action timeout
    pg = ctx.new_page()                                 # Opens new page tab
    pg.goto(f"{BASE_URL}/inventory.html")              # Directly visits protected inventory page
    yield pg                                            # Provides authenticated tab to test
    ctx.close()                                         # Closes context & wipes test-modified state


# =============================================
# CONVENIENCE PAGE OBJECT FIXTURES
# =============================================
# These wrap logged_in_page in a page object so tests
# receive a typed object instead of a raw Page.
# Tests become cleaner: def test_x(inventory: InventoryPage)
# instead of: def test_x(logged_in_page: Page)

@pytest.fixture(scope="function")                       # Runs per test function
def login_page(page: Page) -> LoginPage:                # Fixture for unauthenticated login tests
    """
    Navigate to login page and return a LoginPage object.
    No auth state — this is for testing the login flow itself.
    """
    return LoginPage(page, BASE_URL).navigate()         # Navigates to base URL and returns LoginPage object


@pytest.fixture(scope="function")                       # Runs per test function
def inventory_page(logged_in_page: Page) -> InventoryPage:   # Fixture wrapping authenticated Inventory page
    """Authenticated InventoryPage, ready for interaction."""
    return InventoryPage(logged_in_page, BASE_URL)      # Returns wrapped InventoryPage instance


@pytest.fixture(scope="function")                       # Runs per test function
def cart(logged_in_page: Page) -> CartPage:             # Fixture preparing cart with 1 item pre-added
    """
    Authenticated CartPage with one item (backpack) already added.
    Saves 2 lines in every cart test.
    """
    inv = InventoryPage(logged_in_page, BASE_URL)       # Initializes InventoryPage wrapper
    return inv.add_to_cart(InventoryPage.BACKPACK).go_to_cart() # Adds item and navigates to CartPage


@pytest.fixture(scope="function")                       # Runs per test function
def checkout(logged_in_page: Page) -> CheckoutPage:     # Fixture preparing checkout at Step 1
    """
    Authenticated CheckoutPage on Step 1.
    Backpack already in cart, navigated to checkout.
    """
    inv = InventoryPage(logged_in_page, BASE_URL)       # Initializes InventoryPage wrapper
    cart = inv.add_to_cart(InventoryPage.BACKPACK).go_to_cart() # Adds item and navigates to Cart
    return cart.go_to_checkout()                        # Navigates from cart to CheckoutPage Step 1


# =============================================
# SCREENSHOT ON FAILURE HOOK
# =============================================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Captures a screenshot directly during the failure call phase
    and embeds the image bytes into the pytest-html report.
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)

    # Trigger only on failure during test execution phase
    if rep.when == "call" and rep.failed:
        page_obj = None

        # Un-wrap Page object from direct fixtures or POM classes
        for arg in item.funcargs.values():
            if isinstance(arg, Page):
                page_obj = arg
                break
            for attr in ["page", "_page", "driver"]:
                if hasattr(arg, attr) and isinstance(getattr(arg, attr), Page):
                    page_obj = getattr(arg, attr)
                    break
            if page_obj:
                break

        if page_obj is None:
            logging.warning(f"Screenshot skipped: No Page object found in funcargs ({list(item.funcargs.keys())})")
            return

        try:
            if not page_obj.is_closed():
                os.makedirs(SCREENSHOT_DIR, exist_ok=True)
                screenshot_path = f"{SCREENSHOT_DIR}/FAIL_{item.name}.png"
                
                # 1. Save screenshot to disk AND store raw bytes
                screenshot_bytes = page_obj.screenshot(path=screenshot_path)
                logging.info(f"Failure screenshot saved: {screenshot_path}")

                # 2. Embed base64 image bytes directly into pytest-html
                import pytest_html
                extra = getattr(rep, "extra", [])
                extra.append(pytest_html.extras.image(screenshot_bytes, mime_type="image/png"))
                rep.extra = extra
            else:
                logging.warning("Screenshot skipped: Page was closed before capture")
        except Exception as e:
            logging.warning(f"Failed to capture or attach screenshot: {e}")