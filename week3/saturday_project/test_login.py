# week3/saturday_project/test_login.py
# All login scenarios for saucedemo.com
# Run with: pytest week3/saturday_project/test_login.py -v

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://www.saucedemo.com"

USERNAME = "#user-name"
PASSWORD = "#password"
LOGIN_BTN = "#login-button"
ERROR_MSG = "[data-test='error']"


# =============================================
# HAPPY PATH
# =============================================

def test_valid_login_redirects_to_inventory(login_page: Page):
    login_page.fill(USERNAME, "standard_user")
    login_page.fill(PASSWORD, "secret_sauce")
    login_page.click(LOGIN_BTN)

    expect(login_page).to_have_url(f"{BASE_URL}/inventory.html")


def test_valid_login_shows_products_heading(login_page: Page):
    login_page.fill(USERNAME, "standard_user")
    login_page.fill(PASSWORD, "secret_sauce")
    login_page.click(LOGIN_BTN)

    expect(login_page.locator(".title")).to_have_text("Products")


def test_valid_login_shows_inventory_items(login_page: Page):
    login_page.fill(USERNAME, "standard_user")
    login_page.fill(PASSWORD, "secret_sauce")
    login_page.click(LOGIN_BTN)

    expect(login_page.locator(".inventory_item")).to_have_count(6)


# =============================================
# INVALID CREDENTIALS
# =============================================

def test_wrong_password_shows_error(login_page: Page):
    login_page.fill(USERNAME, "standard_user")
    login_page.fill(PASSWORD, "wrong_password")
    login_page.click(LOGIN_BTN)

    expect(login_page.locator(ERROR_MSG)).to_be_visible()
    expect(login_page.locator(ERROR_MSG)).to_contain_text(
        "Username and password do not match"
    )


def test_wrong_username_shows_error(login_page: Page):
    login_page.fill(USERNAME, "nonexistent_user")
    login_page.fill(PASSWORD, "secret_sauce")
    login_page.click(LOGIN_BTN)

    expect(login_page.locator(ERROR_MSG)).to_be_visible()
    expect(login_page.locator(ERROR_MSG)).to_contain_text(
        "Username and password do not match"
    )


def test_empty_username_shows_required_error(login_page: Page):
    login_page.fill(PASSWORD, "secret_sauce")
    login_page.click(LOGIN_BTN)

    expect(login_page.locator(ERROR_MSG)).to_contain_text(
        "Username is required"
    )


def test_empty_password_shows_required_error(login_page: Page):
    login_page.fill(USERNAME, "standard_user")
    login_page.click(LOGIN_BTN)

    expect(login_page.locator(ERROR_MSG)).to_contain_text(
        "Password is required"
    )


def test_both_fields_empty_shows_username_error(login_page: Page):
    login_page.click(LOGIN_BTN)

    expect(login_page.locator(ERROR_MSG)).to_contain_text(
        "Username is required"
    )


def test_locked_out_user_shows_locked_error(login_page: Page):
    login_page.fill(USERNAME, "locked_out_user")
    login_page.fill(PASSWORD, "secret_sauce")
    login_page.click(LOGIN_BTN)

    expect(login_page.locator(ERROR_MSG)).to_contain_text(
        "Sorry, this user has been locked out"
    )


def test_error_message_has_close_button(login_page: Page):
    login_page.fill(USERNAME, "wrong")
    login_page.fill(PASSWORD, "wrong")
    login_page.click(LOGIN_BTN)

    expect(login_page.locator(ERROR_MSG)).to_be_visible()

    # Close the error
    login_page.locator("[data-test='error-button']").click()

    expect(login_page.locator(ERROR_MSG)).not_to_be_visible()


def test_login_page_has_correct_title(login_page: Page):
    expect(login_page).to_have_title("Swag Labs")


def test_logout_returns_to_login_page(login_page: Page):
    login_page.fill(USERNAME, "standard_user")
    login_page.fill(PASSWORD, "secret_sauce")
    login_page.click(LOGIN_BTN)
    expect(login_page).to_have_url(f"{BASE_URL}/inventory.html")

    # Open burger menu and click logout
    login_page.locator("#react-burger-menu-btn").click()
    login_page.locator("#logout_sidebar_link").click()

    expect(login_page).to_have_url(f"{BASE_URL}/")
    expect(login_page.locator(LOGIN_BTN)).to_be_visible()