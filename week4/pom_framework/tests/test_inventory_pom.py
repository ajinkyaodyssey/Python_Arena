# week4/pom_framework/tests/test_inventory_pom.py
# Inventory tests using POM
# Run with: pytest week4/pom_framework/tests/test_inventory_pom.py -v

import pytest
from week4.pom_framework.pages.inventory_page import InventoryPage


def test_inventory_shows_six_products(inventory_page: InventoryPage):
    inventory_page.expect_item_count(6)


def test_all_product_names_are_non_empty(inventory_page: InventoryPage):
    names = inventory_page.get_all_product_names()
    assert len(names) == 6
    assert all(len(n.strip()) > 0 for n in names)


def test_all_prices_are_positive(inventory_page: InventoryPage):
    prices = inventory_page.get_all_prices()
    assert len(prices) == 6
    assert all(p > 0 for p in prices)


def test_sort_az(inventory_page: InventoryPage):
    inventory_page.sort_az().expect_sorted_az()


def test_sort_za(inventory_page: InventoryPage):
    inventory_page.sort_za().expect_sorted_za()


def test_sort_price_low_high(inventory_page: InventoryPage):
    inventory_page.sort_price_low_high().expect_sorted_price_low_high()


def test_sort_price_high_low(inventory_page: InventoryPage):
    inventory_page.sort_price_high_low().expect_sorted_price_high_low()


def test_add_to_cart_updates_badge(inventory_page: InventoryPage):
    inventory_page.expect_cart_empty()
    inventory_page.add_to_cart(InventoryPage.BACKPACK)
    inventory_page.expect_cart_badge(1)


def test_add_two_items_badge_shows_two(inventory_page: InventoryPage):
    inventory_page.add_to_cart(
        InventoryPage.BACKPACK
    ).add_to_cart(
        InventoryPage.BIKE_LIGHT
    ).expect_cart_badge(2)


def test_get_cart_count_returns_none_when_empty(inventory_page: InventoryPage):
    assert inventory_page.get_cart_count() is None


def test_get_cart_count_returns_correct_number(inventory_page: InventoryPage):
    inventory_page.add_to_cart(InventoryPage.BACKPACK)
    assert inventory_page.get_cart_count() == 1


def test_method_chaining_sort_and_add(inventory_page: InventoryPage):
    """
    Method chaining makes complex flows readable.
    This is one of POM's biggest advantages.
    """
    inventory_page \
        .sort_price_high_low() \
        .expect_sorted_price_high_low() \
        .add_to_cart(InventoryPage.BACKPACK) \
        .expect_cart_badge(1)