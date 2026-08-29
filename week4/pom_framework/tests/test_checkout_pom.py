# week4/pom_framework/tests/test_checkout_pom.py
import pytest
from week4.pom_framework.pages.checkout_page import CheckoutPage
from playwright.sync_api import Page


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


# =============================================
# ADDITIONAL CHECKOUT TESTS (Day 21 Saturday)
# =============================================

def test_checkout_step_one_has_three_fields(
    checkout: CheckoutPage
):
    """
    All three input fields must be present and editable.
    If any field is missing the form cannot be submitted.
    """
    from playwright.sync_api import expect

    first_name = checkout.page.locator("[data-test='firstName']")
    last_name = checkout.page.locator("[data-test='lastName']")
    postal_code = checkout.page.locator("[data-test='postalCode']")

    expect(first_name).to_be_visible()
    expect(first_name).to_be_editable()
    expect(last_name).to_be_visible()
    expect(last_name).to_be_editable()
    expect(postal_code).to_be_visible()
    expect(postal_code).to_be_editable()


def test_checkout_error_closes_after_filling_fields(
    checkout: CheckoutPage
):
    """
    Submit empty form to trigger error.
    Then fill fields and submit again.
    Error should be gone on second submission.
    This tests that validation resets correctly.
    """
    # Trigger validation error
    checkout.continue_to_review()
    checkout.expect_error_containing("First Name is required")

    # Fill correctly and continue
    checkout.fill_and_continue("Divya", "Kumar", "600001")

    # Should now be on step 2 with no error
    checkout.expect_on_step_two()


def test_checkout_review_shows_payment_info(
    checkout: CheckoutPage
):
    """
    Order review page must show payment and shipping info sections.
    These sections tell the user what payment method is being used.
    """
    from playwright.sync_api import expect

    checkout.fill_and_continue("Test", "User", "12345")

    payment_info = checkout.page.locator(".summary_info")
    expect(payment_info).to_be_visible()


def test_complete_checkout_clears_cart(
    logged_in_page: Page
):
    """
    After completing checkout the cart should be empty.
    Verifies the order was actually processed — not just the
    confirmation page shown while cart remains populated.
    """
    from week4.pom_framework.pages.inventory_page import InventoryPage

    inv = InventoryPage(
        logged_in_page, "https://www.saucedemo.com"
    )

    # Add item, complete checkout
    inventory_after = (
        inv.add_to_cart(InventoryPage.BACKPACK)
           .go_to_cart()
           .go_to_checkout()
           .complete_checkout("Divya", "Kumar", "600001")
           .expect_order_complete()
           .back_to_products()
    )

    # Cart should be empty after completed order
    inventory_after.expect_cart_empty()


def test_checkout_item_quantity_shown_in_review(
    checkout: CheckoutPage
):
    """
    The order review must show the item quantity.
    Quantity of 1 for a single item added to cart.
    """
    from playwright.sync_api import expect

    checkout.fill_and_continue("Arjun", "Sharma", "400001")

    quantity = checkout.page.locator(".cart_quantity")
    expect(quantity).to_be_visible()
    expect(quantity).to_have_text("1")