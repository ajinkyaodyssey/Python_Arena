# week4/pom_framework/tests/test_full_flow_pom.py
# End-to-end flows using POM.
# These tests read like a plain English description of what the user does.
# Zero locators. Zero raw Playwright calls.

import pytest
from playwright.sync_api import Page
from week4.pom_framework.pages.login_page import LoginPage
from week4.pom_framework.pages.inventory_page import InventoryPage

BASE_URL = "https://www.saucedemo.com"


# @pytest.mark.smoke
@pytest.mark.ui
def test_complete_purchase_flow(page: Page):
    """
    Full user journey from login to order confirmation.
    Login -> Add item -> Go to cart -> Checkout -> Complete.
    This is the single most important test in the suite.
    """
    (
        LoginPage(page, BASE_URL)
        .navigate()
        .login("standard_user", "secret_sauce")
        .expect_loaded()
        .add_to_cart(InventoryPage.BACKPACK)
        .go_to_cart()
        .expect_item_count(1)
        .go_to_checkout()
        .complete_checkout("Divya", "Kumar", "600001")
        .expect_order_complete()
    )


# @pytest.mark.regression
@pytest.mark.ui
def test_sort_then_buy_most_expensive(page: Page):
    """
    Sort by price high-low, add the first item, complete purchase.
    Tests that sort + cart + checkout work together end-to-end.
    """
    inventory = (
        LoginPage(page, BASE_URL)
        .navigate()
        .login("standard_user", "secret_sauce")
    )

    # Get most expensive item name before adding
    inventory.sort_price_high_low()
    most_expensive = inventory.get_all_product_names()[0]

    # Add it and complete purchase
    (
        inventory
        .add_to_cart(InventoryPage.FLEECE_JACKET)
        .go_to_cart()
        .expect_item_present(most_expensive)
        .go_to_checkout()
        .complete_checkout()
        .expect_order_complete()
    )


# @pytest.mark.regression
@pytest.mark.ui
def test_add_remove_then_buy(page: Page):
    """
    Add two items, remove one, buy the remaining one.
    Tests cart management before checkout.
    """
    (
        LoginPage(page, BASE_URL)
        .navigate()
        .login("standard_user", "secret_sauce")
        .add_to_cart(InventoryPage.BACKPACK)
        .add_to_cart(InventoryPage.BIKE_LIGHT)
        .expect_cart_badge(2)
        .remove_from_the_cart(InventoryPage.BIKE_LIGHT)
        .expect_cart_badge(1)
        .go_to_cart()
        .expect_item_count(1)
        .expect_item_present("Sauce Labs Backpack")
        .expect_item_not_present("Sauce Labs Bike Light")
        .go_to_checkout()
        .complete_checkout("Arjun", "Sharma", "400001")
        .expect_order_complete()
    )


# @pytest.mark.regression
@pytest.mark.ui
def test_logout_and_login_again(page: Page):
    """
    Login, logout, login again. Tests the full auth cycle.
    """
    (
        LoginPage(page, BASE_URL)
        .navigate()
        .login("standard_user", "secret_sauce")
        .expect_loaded()
        .logout()
        .expect_on_login_page()
        .login("standard_user", "secret_sauce")
        .expect_loaded()
    )
