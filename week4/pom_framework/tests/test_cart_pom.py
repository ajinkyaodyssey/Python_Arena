# week4/pom_framework/tests/test_cart_pom.py
import pytest
from week4.pom_framework.pages.inventory_page import InventoryPage
from week4.pom_framework.pages.cart_page import CartPage


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