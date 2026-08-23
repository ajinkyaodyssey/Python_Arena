# week4/pom_framework/tests/test_checkout_pom.py
import pytest
from week4.pom_framework.pages.checkout_page import CheckoutPage


def test_complete_checkout_flow(checkout: CheckoutPage):
    checkout.complete_checkout(
        "Divya", "Kumar", "600001"
    ).expect_order_complete()


def test_order_total_math_is_correct(checkout: CheckoutPage):
    checkout.fill_and_continue(
        "Test", "User", "12345"
    ).expect_total_equals_subtotal_plus_tax()


def test_order_summary_has_backpack(checkout: CheckoutPage):
    checkout.fill_and_continue(
        "Test", "User", "12345"
    ).expect_item_in_summary("Sauce Labs Backpack")


def test_missing_first_name_error(checkout: CheckoutPage):
    checkout.fill_and_continue(
        "", "Kumar", "600001"
    ).expect_error_containing("First Name is required")


def test_missing_last_name_error(checkout: CheckoutPage):
    checkout.fill_and_continue(
        "Divya", "", "600001"
    ).expect_error_containing("Last Name is required")


def test_missing_postal_code_error(checkout: CheckoutPage):
    checkout.fill_and_continue(
        "Divya", "Kumar", ""
    ).expect_error_containing("Postal Code is required")


def test_cancel_from_step_one_goes_to_cart(checkout: CheckoutPage):
    cart = checkout.cancel()
    cart.expect_loaded()


def test_cancel_from_step_two_goes_to_inventory(checkout: CheckoutPage):
    inventory = checkout.fill_and_continue(
        "Test", "User", "12345"
    ).cancel_review()
    inventory.expect_loaded()


def test_back_home_after_order_returns_to_inventory(
    checkout: CheckoutPage
):
    inventory = checkout.complete_checkout().back_to_products()
    inventory.expect_loaded()