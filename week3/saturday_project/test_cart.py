# week3/saturday_project/test_cart.py
# Cart tests: add, remove, quantities, navigation

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://www.saucedemo.com"

CART_BADGE = ".shopping_cart_badge"
CART_ITEM = ".cart_item"
CART_ITEM_NAME = ".inventory_item_name"
CART_ITEM_PRICE = ".inventory_item_price"
REMOVE_BACKPACK_INVENTORY = "[data-test='remove-sauce-labs-backpack']"
ADD_BACKPACK = "[data-test='add-to-cart-sauce-labs-backpack']"
ADD_BIKE_LIGHT = "[data-test='add-to-cart-sauce-labs-bike-light']"
CONTINUE_SHOPPING = "[data-test='continue-shopping']"
CHECKOUT_BTN = "[data-test='checkout']"


def test_cart_shows_added_item(cart_page: Page):
    items = cart_page.locator(CART_ITEM)
    expect(items).to_have_count(1)


def test_cart_item_has_correct_name(cart_page: Page):
    item_name = cart_page.locator(CART_ITEM_NAME).first
    expect(item_name).to_have_text("Sauce Labs Backpack")


def test_cart_item_has_price(cart_page: Page):
    price = cart_page.locator(CART_ITEM_PRICE).first
    price_text = price.text_content()
    assert price_text.startswith("$"), f"Price should start with $, got {price_text}"
    assert float(price_text.replace("$", "")) > 0


def test_cart_item_has_quantity_of_one(cart_page: Page):
    quantity = cart_page.locator(".cart_quantity").first
    expect(quantity).to_have_text("1")


def test_remove_item_from_cart(cart_page: Page):
    expect(cart_page.locator(CART_ITEM)).to_have_count(1)

    cart_page.locator("[data-test='remove-sauce-labs-backpack']").click()

    expect(cart_page.locator(CART_ITEM)).to_have_count(0)


def test_removing_item_clears_cart_badge(cart_page: Page):
    badge = cart_page.locator(CART_BADGE)
    expect(badge).to_be_visible()

    cart_page.locator("[data-test='remove-sauce-labs-backpack']").click()

    expect(badge).not_to_be_visible()


def test_continue_shopping_returns_to_inventory(cart_page: Page):
    cart_page.locator(CONTINUE_SHOPPING).click()

    expect(cart_page).to_have_url(f"{BASE_URL}/inventory.html")
    expect(cart_page.locator(".inventory_list")).to_be_visible()


def test_multiple_items_in_cart(inventory_page: Page):
    inventory_page.locator(ADD_BACKPACK).click()
    inventory_page.locator(ADD_BIKE_LIGHT).click()

    inventory_page.locator(".shopping_cart_link").click()

    expect(inventory_page.locator(CART_ITEM)).to_have_count(2)
    expect(inventory_page.locator(CART_BADGE)).to_have_text("2")


def test_cart_persists_after_navigating_back(inventory_page: Page):
    inventory_page.locator(ADD_BACKPACK).click()
    inventory_page.locator(".shopping_cart_link").click()
    expect(inventory_page.locator(CART_ITEM)).to_have_count(1)

    # Go back to inventory
    inventory_page.locator(CONTINUE_SHOPPING).click()

    # Navigate to cart again
    inventory_page.locator(".shopping_cart_link").click()

    # Item should still be there
    expect(inventory_page.locator(CART_ITEM)).to_have_count(1)


def test_checkout_button_navigates_to_checkout(cart_page: Page):
    cart_page.locator(CHECKOUT_BTN).click()

    expect(cart_page).to_have_url(f"{BASE_URL}/checkout-step-one.html")