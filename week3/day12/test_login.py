# week3/day12/test_login.py
# First Playwright tests against saucedemo.com
# Run with: pytest week3/day12/test_login.py -v

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://www.saucedemo.com"

# Locators - defined once at the top, not scattered through tests
USERNAME_INPUT = "#user-name"
PASSWORD_INPUT = "#password"
LOGIN_BUTTON = "#login-button"
ERROR_MESSAGE = "[data-test='error']"
PAGE_TITLE = ".title"
INVENTORY_ITEM = ".inventory_item"


# =============================================
# TEST 1: Valid login navigates to inventory
# =============================================

def test_valid_login_navigates_to_inventory(login_page: Page):
    """
    GIVEN a user on the login page
    WHEN they enter valid credentials
    THEN they should be redirected to the inventory page
    """
    login_page.fill(USERNAME_INPUT, "standard_user")
    login_page.fill(PASSWORD_INPUT, "secret_sauce")
    login_page.click(LOGIN_BUTTON)

    # Assert URL changed to inventory
    expect(login_page).to_have_url(f"{BASE_URL}/inventory.html")


# =============================================
# TEST 2: Valid login shows Products title
# =============================================

def test_valid_login_shows_inventory_title(login_page: Page):
    """
    GIVEN a user who logs in successfully
    WHEN the inventory page loads
    THEN the page title should show 'Products'
    """
    login_page.fill(USERNAME_INPUT, "standard_user")
    login_page.fill(PASSWORD_INPUT, "secret_sauce")
    login_page.click(LOGIN_BUTTON)

    expect(login_page).to_have_url(f"{BASE_URL}/inventory.html")
    expect(login_page.locator(PAGE_TITLE)).to_have_text("Products")


# =============================================
# TEST 3: Wrong password shows error message
# =============================================

def test_wrong_password_shows_error(login_page: Page):
    """
    GIVEN a user on the login page
    WHEN they enter a valid username but wrong password
    THEN an error message should appear
    AND the URL should remain on the login page
    """
    login_page.fill(USERNAME_INPUT, "standard_user")
    login_page.fill(PASSWORD_INPUT, "wrong_password_123")
    login_page.click(LOGIN_BUTTON)

    # Error message should be visible
    expect(login_page.locator(ERROR_MESSAGE)).to_be_visible()

    # Error should contain the expected text
    expect(login_page.locator(ERROR_MESSAGE)).to_contain_text(
        "Username and password do not match"
    )

    # Should still be on login page
    expect(login_page).to_have_url(BASE_URL + "/")


# =============================================
# TEST 4: Wrong username shows error message
# =============================================

def test_wrong_username_shows_error(login_page: Page):
    """
    GIVEN a user on the login page
    WHEN they enter a non-existent username
    THEN an error message should appear
    """
    login_page.fill(USERNAME_INPUT, "nonexistent_user_xyz")
    login_page.fill(PASSWORD_INPUT, "secret_sauce")
    login_page.click(LOGIN_BUTTON)

    expect(login_page.locator(ERROR_MESSAGE)).to_be_visible()
    expect(login_page.locator(ERROR_MESSAGE)).to_contain_text(
        "Username and password do not match"
    )


# =============================================
# TEST 5: Empty username shows required error
# =============================================

def test_empty_username_shows_required_error(login_page: Page):
    """
    GIVEN a user on the login page
    WHEN they click login without entering a username
    THEN an error should say username is required
    """
    # Leave username empty, only fill password
    login_page.fill(PASSWORD_INPUT, "secret_sauce")
    login_page.click(LOGIN_BUTTON)

    expect(login_page.locator(ERROR_MESSAGE)).to_be_visible()
    expect(login_page.locator(ERROR_MESSAGE)).to_contain_text(
        "Username is required"
    )


# =============================================
# TEST 6: Empty password shows required error
# =============================================

def test_empty_password_shows_required_error(login_page: Page):
    """
    GIVEN a user on the login page
    WHEN they enter a username but no password
    THEN an error should say password is required
    """
    login_page.fill(USERNAME_INPUT, "standard_user")
    # Leave password empty
    login_page.click(LOGIN_BUTTON)

    expect(login_page.locator(ERROR_MESSAGE)).to_be_visible()
    expect(login_page.locator(ERROR_MESSAGE)).to_contain_text(
        "Password is required"
    )


# =============================================
# TEST 7: Locked out user gets specific error
# =============================================

def test_locked_out_user_gets_specific_error(login_page: Page):
    """
    GIVEN a locked out user
    WHEN they attempt to login with correct credentials
    THEN they should see a locked out message
    """
    login_page.fill(USERNAME_INPUT, "locked_out_user")
    login_page.fill(PASSWORD_INPUT, "secret_sauce")
    login_page.click(LOGIN_BUTTON)

    expect(login_page.locator(ERROR_MESSAGE)).to_be_visible()
    expect(login_page.locator(ERROR_MESSAGE)).to_contain_text(
        "Sorry, this user has been locked out"
    )