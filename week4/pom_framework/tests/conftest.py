# week4/pom_framework/tests/conftest.py
import pytest
import os
from playwright.sync_api import sync_playwright, Page, Browser

from week4.pom_framework.pages.login_page import LoginPage
from week4.pom_framework.pages.inventory_page import InventoryPage

BASE_URL = "https://www.saucedemo.com"
AUTH_STATE = "/tmp/pom_auth_state.json"
VALID_USER = "standard_user"
VALID_PASS = "secret_sauce"


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True)
        yield br
        br.close()


@pytest.fixture(scope="function")
def page(browser: Browser) -> Page:
    ctx = browser.new_context(viewport={"width": 1280, "height": 720})
    ctx.set_default_timeout(20_000)
    pg = ctx.new_page()
    yield pg
    ctx.close()


@pytest.fixture(scope="session")
def auth_state(browser: Browser) -> str:
    """Login once, save auth state for all POM tests."""
    if not os.path.exists(AUTH_STATE):
        ctx = browser.new_context()
        pg = ctx.new_page()
        pg.set_default_timeout(20_000)
        LoginPage(pg, BASE_URL).navigate().login(VALID_USER, VALID_PASS)
        pg.wait_for_url(f"{BASE_URL}/inventory.html")
        ctx.storage_state(path=AUTH_STATE)
        ctx.close()
    return AUTH_STATE


@pytest.fixture(scope="function")
def login_page(page: Page) -> LoginPage:
    """Navigate to login page and return a LoginPage object."""
    return LoginPage(page, BASE_URL).navigate()


@pytest.fixture(scope="function")
def inventory_page(browser: Browser, auth_state: str) -> InventoryPage:
    """Authenticated InventoryPage — no login flow."""
    ctx = browser.new_context(
        storage_state=auth_state,
        viewport={"width": 1280, "height": 720}
    )
    ctx.set_default_timeout(20_000)
    pg = ctx.new_page()
    inv = InventoryPage(pg, BASE_URL).navigate()
    yield inv
    ctx.close()
    

# HOOK: captures the result/report of each test phase
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # Pause here → let Pytest run and create the test report
    outcome = yield

    # Get the actual test report/result
    rep = outcome.get_result()

    # Store report on the test: rep_setup / rep_call / rep_teardown
    setattr(item, f"rep_{rep.when}", rep)


# FIXTURE: runs automatically for every test

@pytest.fixture(autouse=True)
def capture_failure(request):

    # Let the test run first; code after yield runs after the test
    yield

    # Check: does the test have a report AND did the actual test fail?
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:

        # Find the page object used by the test
        page_obj = (
            request.node.funcargs.get("login_page") or
            request.node.funcargs.get("inventory_page")
        )

        # If a page object was found, take a screenshot
        if page_obj:
            # Screenshot name = FAIL_<test name>
            page_obj.take_screenshot(
                f"FAIL_{request.node.name}"
            )
            
# HOOK
#   ↓
# Get test report
#   ↓
# Store as rep_call
#   ↓
# FIXTURE runs automatically
#   ↓
# yield → let test finish
#   ↓
# Check rep_call.failed
#   ↓
# Find page object
#   ↓
# Take screenshot            