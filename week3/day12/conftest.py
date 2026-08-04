# week3/day12/conftest.py
import pytest
from playwright.sync_api import sync_playwright, Page, Browser


BASE_URL = "https://www.saucedemo.com"


@pytest.fixture(scope="session")        # Runs ONCE per test run
def browser_instance():
    """
    One browser for the entire test session.
    Session scope = created once, reused by all tests.
    Closed when all tests finish.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser       
        browser.close()


@pytest.fixture(scope="function")       # Runs ONCE per test case
def page(browser_instance: Browser) -> Page:
    """
    Fresh browser context and page for EVERY test.
    Function scope = new context per test so tests never share state.
    Cookies, localStorage, session — all wiped between tests.
    """
    context = browser_instance.new_context(
        viewport={"width": 1280, "height": 720}
    )
    page = context.new_page()
    page.set_default_timeout(15_000)    # 15 seconds max wait per action
    yield page      # <--- Execution pauses here during test execution
    context.close()     # <--- Runs AFTER the test finishes


@pytest.fixture(scope="function")
def login_page(page: Page) -> Page:
    """
    Page already navigated to the login URL.
    Use this fixture when your test starts at the login page.
    """
    page.goto(BASE_URL)
    return page