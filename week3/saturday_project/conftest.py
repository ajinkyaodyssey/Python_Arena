# week3/saturday_project/conftest.py
# Shared fixtures for the full saucedemo test suite

import pytest
import os
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext

BASE_URL = "https://www.saucedemo.com"
STANDARD_USER = "standard_user"
LOCKED_USER = "locked_out_user"
PROBLEM_USER = "problem_user"
VALID_PASSWORD = "secret_sauce"
AUTH_STATE_FILE = "/tmp/saucedemo_auth.json"


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True)
        yield br
        br.close()


@pytest.fixture(scope="function")
def context(browser: Browser) -> BrowserContext:
    ctx = browser.new_context(viewport={"width": 1280, "height": 720})
    ctx.set_default_timeout(20_000)
    yield ctx
    ctx.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Page:
    pg = context.new_page()
    yield pg


@pytest.fixture(scope="function")
def login_page(page: Page) -> Page:
    """Navigate to login page."""
    page.goto(BASE_URL)
    return page


# =============================================
# SESSION AUTH STATE
# =============================================

@pytest.fixture(scope="session")
def auth_state(browser: Browser) -> str:
    """Log in once, save state. Reused by all inventory/cart/checkout tests."""
    if not os.path.exists(AUTH_STATE_FILE):
        ctx = browser.new_context()
        pg = ctx.new_page()
        pg.set_default_timeout(20_000)
        pg.goto(BASE_URL)
        pg.fill("#user-name", STANDARD_USER)
        pg.fill("#password", VALID_PASSWORD)
        pg.click("#login-button")
        pg.wait_for_url(f"{BASE_URL}/inventory.html")
        ctx.storage_state(path=AUTH_STATE_FILE)
        ctx.close()
    return AUTH_STATE_FILE


@pytest.fixture(scope="function")
def inventory_page(browser: Browser, auth_state: str) -> Page:
    """Authenticated page on inventory. No login flow per test."""
    ctx = browser.new_context(
        storage_state=auth_state,
        viewport={"width": 1280, "height": 720}
    )
    ctx.set_default_timeout(20_000)
    pg = ctx.new_page()
    pg.goto(f"{BASE_URL}/inventory.html")
    yield pg
    ctx.close()


@pytest.fixture(scope="function")
def cart_page(browser: Browser, auth_state: str) -> Page:
    """Authenticated page with one item already in cart."""
    ctx = browser.new_context(
        storage_state=auth_state,
        viewport={"width": 1280, "height": 720}
    )
    ctx.set_default_timeout(20_000)
    pg = ctx.new_page()
    pg.goto(f"{BASE_URL}/inventory.html")

    # Add backpack to cart
    pg.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()
    pg.locator(".shopping_cart_link").click()
    pg.wait_for_url(f"{BASE_URL}/cart.html")

    yield pg
    ctx.close()