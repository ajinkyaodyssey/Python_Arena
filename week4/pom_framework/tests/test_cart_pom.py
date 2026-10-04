# week4/pom_framework/tests/test_cart_pom.py
import pytest
from week4.pom_framework.pages.inventory_page import InventoryPage
from week4.pom_framework.pages.cart_page import CartPage
from playwright.sync_api import Page


def test_cart_shows_added_item(cart: CartPage):
    cart.expect_item_count(1)


def test_cart_item_is_backpack(cart: CartPage):
    cart.expect_item_present("Sauce Labs Backpack")


def test_cart_item_quantity_is_one(cart: CartPage):
    assert cart.get_item_quantity(0) == 1


def test_cart_item_price_is_positive(cart: CartPage):
    prices = cart.get_item_prices()
    assert all(p > 0 for p in prices)


def test_remove_item_empties_cart(cart: CartPage):
    cart.remove_item(
        InventoryPage.BACKPACK
    ).expect_empty()


def test_continue_shopping_returns_to_inventory(cart: CartPage):
    inventory = cart.continue_shopping()
    inventory.expect_loaded()


def test_checkout_button_goes_to_checkout(cart: CartPage):
    checkout = cart.go_to_checkout()
    checkout.expect_on_step_one()


def test_two_items_in_cart(logged_in_page):
    from week4.pom_framework.pages.inventory_page import InventoryPage
    inv = InventoryPage(logged_in_page, "https://www.saucedemo.com")
    cart = (
        inv.add_to_cart(InventoryPage.BACKPACK)
           .add_to_cart(InventoryPage.BIKE_LIGHT)
           .go_to_cart()
    )
    cart.expect_item_count(2)


# =============================================
# ADDITIONAL CART TESTS (Day 21 Saturday)
# =============================================

def test_cart_title_is_your_cart(cart: CartPage):
    """
    Verify the cart page heading is correct.
    Catches regressions where navigation lands on wrong page.
    """
    cart.expect_loaded()


def test_remove_item_updates_cart_correctly(
    logged_in_page: Page
):
    """
    Add two items. Remove one. Verify the correct one remains.
    Tests that remove targets the right item, not just any item.
    """
    from week4.pom_framework.pages.inventory_page import InventoryPage
    from week4.pom_framework.pages.cart_page import CartPage

    inv = InventoryPage(logged_in_page, "https://www.saucedemo.com")
    cart = (
        inv.add_to_cart(InventoryPage.BACKPACK)
           .add_to_cart(InventoryPage.BIKE_LIGHT)
           .go_to_cart()
    )

    # Remove only the bike light
    cart.remove_item(InventoryPage.BIKE_LIGHT)

    # Backpack should still be there
    cart.expect_item_count(1)
    cart.expect_item_present("Sauce Labs Backpack")
    cart.expect_item_not_present("Sauce Labs Bike Light")


def test_cart_badge_disappears_after_removing_all_items(
    logged_in_page: Page
):
    """
    Add one item, go to cart, remove it.
    Cart badge should disappear completely — not show 0.
    Difference: badge is hidden vs badge shows zero.
    """
    from week4.pom_framework.pages.inventory_page import InventoryPage

    inv = InventoryPage(logged_in_page, "https://www.saucedemo.com")
    inv.add_to_cart(InventoryPage.BACKPACK)
    inv.expect_cart_badge(1)

    cart = inv.go_to_cart()
    cart.remove_item(InventoryPage.BACKPACK)
    cart.expect_empty()

    # Go back to inventory and verify badge is gone
    inventory = cart.continue_shopping()
    inventory.expect_cart_empty()


def test_cart_item_price_matches_inventory_price(
    logged_in_page: Page
):
    """
    Price shown in cart must match expected backpack price.
    Backpack on saucedemo is always 29.99.
    """
    from week4.pom_framework.pages.inventory_page import InventoryPage

    inv = InventoryPage(logged_in_page, "https://www.saucedemo.com")
    cart = inv.add_to_cart(InventoryPage.BACKPACK).go_to_cart()

    cart_prices = cart.get_item_prices()

    assert len(cart_prices) == 1, (
        f"Expected 1 item in cart, got {len(cart_prices)}"
    )
    assert cart_prices[0] == 29.99, (
        f"Backpack should cost 29.99, got {cart_prices[0]}"
    )

def test_cart_page_has_continue_and_checkout_buttons(
    cart: CartPage
):
    """
    Both action buttons must be present and enabled.
    If either is missing the user is stuck on the cart page.
    """
    from playwright.sync_api import expect

    # Access the raw page through the cart fixture
    continue_btn = cart.page.locator(
        "[data-test='continue-shopping']"
    )
    checkout_btn = cart.page.locator("[data-test='checkout']")

    expect(continue_btn).to_be_visible()
    expect(continue_btn).to_be_enabled()
    expect(checkout_btn).to_be_visible()
    expect(checkout_btn).to_be_enabled()