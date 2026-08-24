# week4/pom_framework/tests/test_login_pom.py
# Login tests using POM — compare with week3/saturday_project/test_login.py
# Notice: zero locators in this file. Zero CSS selectors.
# Run with: pytest week4/pom_framework/tests/test_login_pom.py -v

import pytest
from playwright.sync_api import expect
from week4.pom_framework.pages.login_page import LoginPage
from week4.pom_framework.pages.inventory_page import InventoryPage

BASE_URL = "https://www.saucedemo.com"


# =============================================
# HAPPY PATH
# =============================================

# @pytest.mark.smoke
def test_valid_login_reaches_inventory(login_page: LoginPage):
    """
    Before POM: 5 lines with raw locators.
    After POM: 2 lines of readable English.
    """
    inventory = login_page.login("standard_user", "secret_sauce")
    inventory.expect_loaded()


# @pytest.mark.smoke
def test_valid_login_shows_six_products(login_page: LoginPage):
    inventory = login_page.login("standard_user", "secret_sauce")
    inventory.expect_item_count(6)


def test_valid_login_cart_starts_empty(login_page: LoginPage):
    inventory = login_page.login("standard_user", "secret_sauce")
    inventory.expect_cart_empty()


# =============================================
# INVALID CREDENTIALS
# =============================================

# @pytest.mark.smoke
def test_wrong_password_shows_error(login_page: LoginPage):
    login_page.login_expecting_failure(
        "standard_user", "wrong_password"
    ).expect_error_containing("Username and password do not match")


# @pytest.mark.regression
def test_wrong_username_shows_error(login_page: LoginPage):
    login_page.login_expecting_failure(
        "nonexistent_user", "secret_sauce"
    ).expect_error_containing("Username and password do not match")


# @pytest.mark.regression
def test_empty_username_shows_required_error(login_page: LoginPage):
    login_page.login_expecting_failure(
        "", "secret_sauce"
    ).expect_error_containing("Username is required")


# @pytest.mark.regression
def test_empty_password_shows_required_error(login_page: LoginPage):
    login_page.login_expecting_failure(
        "standard_user", ""
    ).expect_error_containing("Password is required")


# @pytest.mark.regression
def test_locked_user_shows_locked_error(login_page: LoginPage):
    login_page.login_expecting_failure(
        "locked_out_user", "secret_sauce"
    ).expect_error_containing("Sorry, this user has been locked out")


# @pytest.mark.regression
def test_error_closes_when_x_clicked(login_page: LoginPage):
    login_page.login_expecting_failure("wrong", "wrong")
    assert login_page.is_error_visible()

    login_page.close_error()

    login_page.expect_error_not_visible()


# @pytest.mark.regression
def test_failed_login_stays_on_login_page(login_page: LoginPage):
    login_page.login_expecting_failure(
        "wrong", "wrong"
    ).expect_on_login_page()


# @pytest.mark.smoke
def test_login_page_title_is_swag_labs(login_page: LoginPage):
    login_page.expect_title("Swag Labs")