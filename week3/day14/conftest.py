# week3/day14/conftest.py       #conftest.py is a special filename recognized by pytest. You should not rename it if you want pytest to automatically discover its fixtures.
import pytest
from playwright.sync_api import sync_playwright, Page, Browser

SAUCE_URL = "https://www.saucedemo.com"
INTERNET_URL = "https://the-internet.herokuapp.com"


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def page(browser: Browser) -> Page:
    context = browser.new_context(viewport={"width": 1280, "height": 720})
    pg = context.new_page()
    pg.set_default_timeout(20_000)
    yield pg
    context.close()


@pytest.fixture(scope="function")
def sauce_login(page: Page) -> Page:
    """Already logged into saucedemo, on inventory page."""
    page.goto(SAUCE_URL)
    page.fill("#user-name", "standard_user")
    page.fill("#password", "secret_sauce")
    page.click("#login-button")
    page.wait_for_url(f"{SAUCE_URL}/inventory.html")
    return page


@pytest.fixture(scope="function")
def internet(page: Page) -> Page:
    """Page pointed at the-internet.herokuapp.com base URL."""
    page.goto(INTERNET_URL)
    return page