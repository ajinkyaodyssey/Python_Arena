# week3/day15/conftest.py
import pytest
from playwright.sync_api import sync_playwright, Page

SAUCE_URL = "https://www.saucedemo.com"
INTERNET_URL = "https://the-internet.herokuapp.com"


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def page(browser):
    context = browser.new_context(viewport={"width": 1280, "height": 720})
    pg = context.new_page()
    pg.set_default_timeout(20_000)
    yield pg
    context.close()


@pytest.fixture(scope="function")
def login_page(page):
    page.goto(SAUCE_URL)
    return page


@pytest.fixture(scope="function")
def inventory_page(page):
    page.goto(SAUCE_URL)
    page.fill("#user-name", "standard_user")
    page.fill("#password", "secret_sauce")
    page.click("#login-button")
    page.wait_for_url(f"{SAUCE_URL}/inventory.html")
    return page