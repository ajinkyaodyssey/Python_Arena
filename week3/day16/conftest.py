# week3/day16/conftest.py
import pytest
import os
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext

SAUCE_URL = "https://www.saucedemo.com"
INTERNET_URL = "https://the-internet.herokuapp.com"
AUTH_STATE_PATH = "/tmp/sauce_auth_state.json"             # File where login state is saved


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)          # Launch Chromium once per test session
        yield browser                                       # Give browser object to tests/fixtures
        browser.close()                                     # Close browser after entire session


@pytest.fixture(scope="function")
def context(browser: Browser) -> BrowserContext:
    ctx = browser.new_context(viewport={"width": 1280, "height": 720})  # Fresh isolated context per test
    ctx.set_default_timeout(20_000)                         # Default timeout = 20 seconds
    yield ctx                                                # Give context to the test
    ctx.close()                                               # Cleanup context after each test


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Page:
    pg = context.new_page()                                  # Create a new tab/page
    yield pg                                                 # Give page to the test


# =============================================
# AUTH STATE FIXTURE
# =============================================
# This is the key fixture for storage state.
# It logs in ONCE per session, saves state to a file,
# and all subsequent tests load from that file.

@pytest.fixture(scope="session")
def auth_state_path(browser: Browser) -> str:
    """
    Logs into saucedemo ONCE for the entire test session.
    Saves cookies + localStorage to a JSON file.
    Returns the path so other fixtures can load it.
    """
    # Only create if it doesn't exist yet
    if not os.path.exists(AUTH_STATE_PATH):                 # Avoid logging in again if state file exists
        ctx = browser.new_context()                         # Separate context only for login
        pg = ctx.new_page()                                 # Create login page

        pg.goto(SAUCE_URL)                                  # Open SauceDemo
        pg.fill("#user-name", "standard_user")              # Enter username
        pg.fill("#password", "secret_sauce")                # Enter password
        pg.click("#login-button")                           # Perform login
        pg.wait_for_url(f"{SAUCE_URL}/inventory.html")      # Confirm login succeeded

        # Save everything: cookies, localStorage, sessionStorage
        ctx.storage_state(path=AUTH_STATE_PATH)             # Save authentication state as JSON
        print(f"\n  [AUTH] State saved to {AUTH_STATE_PATH}")

        ctx.close()                                         # Close temporary login context

    return AUTH_STATE_PATH                                  # Return saved state file path


@pytest.fixture(scope="function")
def authenticated_page(browser: Browser, auth_state_path: str) -> Page:
    """
    Creates a new context loaded with the saved auth state.
    This page starts already logged in — no login flow needed.
    """
    ctx = browser.new_context(
        storage_state=auth_state_path,                      # Load saved cookies/localStorage → already logged in
        viewport={"width": 1280, "height": 720}             # Set browser viewport
    )
    ctx.set_default_timeout(20_000)                         # Default timeout = 20 seconds
    pg = ctx.new_page()                                     # Create page inside authenticated context
    pg.goto(f"{SAUCE_URL}/inventory.html")                  # Go directly to inventory after restoring login
    yield pg                                                 # Give authenticated page to the test
    ctx.close()                                               # Cleanup context after test