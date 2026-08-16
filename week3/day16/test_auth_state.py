# week3/day16/test_auth_state.py
# Storage state: save and reuse authentication across tests
# Run with: pytest week3/day16/test_auth_state.py -v -s

import os
import json
import time
import pytest
from playwright.sync_api import Page, Browser, expect

SAUCE_URL = "https://www.saucedemo.com"
AUTH_STATE_PATH = "/tmp/sauce_auth_state.json"


def test_auth_state_file_is_created(auth_state_path: str):
    """
    Verify the auth state file exists and contains expected data.
    The auth state file is a JSON file containing:
    - cookies: all cookies set during the login session
    - origins: localStorage and sessionStorage for each origin
    """
    assert os.path.exists(auth_state_path), \
        f"Auth state file not found at {auth_state_path}"

    with open(auth_state_path) as f:
        state = json.load(f)        # It opens the JSON file and converts the JSON into a Python dictionary

    print(f"\n  [AUTH STATE] File location: {auth_state_path}")
    print(f"  [AUTH STATE] Keys in file: {list(state.keys())}")
    print(f"  [AUTH STATE] Cookie count: {len(state.get('cookies', []))}")      # It gets cookies from the dictionary. If the key doesn't exist, it returns an empty list
    print(f"  [AUTH STATE] Origin count: {len(state.get('origins', []))}")

    # Auth state should have cookies section
    assert "cookies" in state or "origins" in state, \
        "Auth state file should contain cookies or origins"
        

def test_authenticated_page_can_add_to_cart(authenticated_page: Page):
    """
    Verify authenticated session is fully functional.
    Adding to cart requires a valid logged-in session.
    If auth state is stale or corrupted, this would fail.
    """
    badge = authenticated_page.locator(".shopping_cart_badge")
    expect(badge).not_to_be_visible()

    authenticated_page.locator(
        "[data-test='add-to-cart-sauce-labs-backpack']"
    ).click()

    expect(badge).to_be_visible()
    expect(badge).to_have_text("1")

    print(f"\n  [AUTH] Cart action worked with loaded auth state")
    print(f"  [AUTH] Badge: '{badge.text_content()}'")
    
    
def test_auth_state_speed_advantage(browser: Browser, auth_state_path: str):
    """
    Demonstrates the speed difference between:
    1. Full login flow (fill, click, wait for navigation)
    2. Loading auth state from file

    In a 50-test suite, this difference compounds significantly.
    """
    # Method 1: Full login flow
    start = time.perf_counter()
    ctx1 = browser.new_context()
    pg1 = ctx1.new_page()
    pg1.set_default_timeout(20_000)
    pg1.goto(SAUCE_URL)
    pg1.fill("#user-name", "standard_user")
    pg1.fill("#password", "secret_sauce")
    pg1.click("#login-button")
    pg1.wait_for_url(f"{SAUCE_URL}/inventory.html")
    login_flow_time = time.perf_counter() - start
    ctx1.close()

    # Method 2: Load from auth state
    start = time.perf_counter()
    ctx2 = browser.new_context(storage_state=auth_state_path)       #Create a new browser context that starts with the authentication state saved in auth_state_path
    pg2 = ctx2.new_page()
    pg2.set_default_timeout(20_000)
    pg2.goto(f"{SAUCE_URL}/inventory.html")
    expect(pg2).to_have_url(f"{SAUCE_URL}/inventory.html")
    auth_state_time = time.perf_counter() - start
    ctx2.close()

    print(f"\n  [SPEED] Full login flow:     {login_flow_time:.3f}s")
    print(f"  [SPEED] Auth state load:     {auth_state_time:.3f}s")
    saving = login_flow_time - auth_state_time
    print(f"  [SPEED] Time saved per test: {saving:.3f}s")
    print(f"  [SPEED] Saved across 50 tests: {saving * 50:.1f}s")


def test_multiple_authenticated_sessions_are_independent(
    browser: Browser, auth_state_path: str
):
    """
    Each context created from the same auth state is independent.
    Adding to cart in session 1 does not affect session 2.
    This proves that storage_state= gives you a COPY of the state,
    not a shared reference.
    """
    # Session 1
    ctx1 = browser.new_context(storage_state=auth_state_path)
    pg1 = ctx1.new_page()
    pg1.set_default_timeout(20_000)
    pg1.goto(f"{SAUCE_URL}/inventory.html")

    # Session 2 - independent
    ctx2 = browser.new_context(storage_state=auth_state_path)
    pg2 = ctx2.new_page()
    pg2.set_default_timeout(20_000)
    pg2.goto(f"{SAUCE_URL}/inventory.html")

    # Add item in session 1 only
    pg1.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()
    expect(pg1.locator(".shopping_cart_badge")).to_have_text("1")

    # Session 2 should be unaffected
    expect(pg2.locator(".shopping_cart_badge")).not_to_be_visible()

    print("\n  [ISOLATION] Session 1 cart: 1 item")
    print("  [ISOLATION] Session 2 cart: 0 items (independent)")

    ctx1.close()
    ctx2.close()