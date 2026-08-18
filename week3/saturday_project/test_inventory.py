# week3/saturday_project/test_inventory.py
# Inventory page tests: product listing, sorting, product details

import pytest
import re
from playwright.sync_api import Page, expect

BASE_URL = "https://www.saucedemo.com"

SORT_DROPDOWN = "[data-test='product-sort-container']"
ITEM_NAME = ".inventory_item_name"
ITEM_PRICE = ".inventory_item_price"
ITEM_DESC = ".inventory_item_desc"
ADD_BACKPACK = "[data-test='add-to-cart-sauce-labs-backpack']"
CART_BADGE = ".shopping_cart_badge"


def test_inventory_shows_six_products(inventory_page: Page):
    expect(inventory_page.locator(".inventory_item")).to_have_count(6)


def test_all_products_have_name_price_and_description(inventory_page: Page):
    names = inventory_page.locator(ITEM_NAME).all_text_contents()
    prices = inventory_page.locator(ITEM_PRICE).all_text_contents()
    descs = inventory_page.locator(ITEM_DESC).all_text_contents()

    assert len(names) == 6
    assert len(prices) == 6
    assert len(descs) == 6

    for name in names:
        assert len(name.strip()) > 0, f"Empty product name found"

    for price in prices:
        assert price.startswith("$"), f"Price '{price}' does not start with $"


def test_sort_by_name_a_to_z(inventory_page: Page):
    inventory_page.locator(SORT_DROPDOWN).select_option(value="az")

    names = inventory_page.locator(ITEM_NAME).all_text_contents()
    assert names == sorted(names), \
        f"Products not sorted A-Z. Got: {names}"


def test_sort_by_name_z_to_a(inventory_page: Page):
    inventory_page.locator(SORT_DROPDOWN).select_option(value="za")

    names = inventory_page.locator(ITEM_NAME).all_text_contents()
    assert names == sorted(names, reverse=True), \
        f"Products not sorted Z-A. Got: {names}"


def test_sort_by_price_low_to_high(inventory_page: Page):
    inventory_page.locator(SORT_DROPDOWN).select_option(value="lohi")

    prices = inventory_page.locator(ITEM_PRICE).all_text_contents()
    price_values = [float(p.replace("$", "")) for p in prices]

    assert price_values == sorted(price_values), \
        f"Prices not sorted low-high. Got: {price_values}"


def test_sort_by_price_high_to_low(inventory_page: Page):
    inventory_page.locator(SORT_DROPDOWN).select_option(value="hilo")

    prices = inventory_page.locator(ITEM_PRICE).all_text_contents()
    price_values = [float(p.replace("$", "")) for p in prices]

    assert price_values == sorted(price_values, reverse=True), \
        f"Prices not sorted high-low. Got: {price_values}"


def test_add_to_cart_button_changes_to_remove(inventory_page: Page):
    add_btn = inventory_page.locator(ADD_BACKPACK)
    expect(add_btn).to_have_text("Add to cart")

    add_btn.click()

    remove_btn = inventory_page.locator(
        "[data-test='remove-sauce-labs-backpack']"
    )
    expect(remove_btn).to_have_text("Remove")


def test_cart_badge_increments_on_add(inventory_page: Page):
    badge = inventory_page.locator(CART_BADGE)
    expect(badge).not_to_be_visible()

    inventory_page.locator(ADD_BACKPACK).click()
    expect(badge).to_have_text("1")

    inventory_page.locator(
        "[data-test='add-to-cart-sauce-labs-bike-light']"
    ).click()
    expect(badge).to_have_text("2")


def test_clicking_product_name_opens_detail_page(inventory_page: Page):
    first_product_name = inventory_page.locator(
        ITEM_NAME
    ).first.text_content()

    inventory_page.locator(ITEM_NAME).first.click()

    # Use regex instead of lambda
    expect(inventory_page).to_have_url(
        re.compile(r"inventory-item")
    )
    expect(
        inventory_page.locator(".inventory_details_name")
    ).to_have_text(first_product_name)


def test_back_button_on_product_detail_returns_to_inventory(
    inventory_page: Page
):
    inventory_page.locator(ITEM_NAME).first.click()

    expect(inventory_page).to_have_url(
        re.compile(r"inventory-item")
    )

    inventory_page.locator("[data-test='back-to-products']").click()

    expect(inventory_page).to_have_url(f"{BASE_URL}/inventory.html")
    expect(inventory_page.locator(".inventory_list")).to_be_visible()