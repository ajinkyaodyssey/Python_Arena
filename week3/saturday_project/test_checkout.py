# week3/saturday_project/test_checkout.py
# Checkout flow: complete purchase and validation errors

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://www.saucedemo.com"

FIRST_NAME = "[data-test='firstName']"
LAST_NAME = "[data-test='lastName']"
POSTAL_CODE = "[data-test='postalCode']"
CONTINUE_BTN = "[data-test='continue']"
FINISH_BTN = "[data-test='finish']"
ERROR_MSG = "[data-test='error']"
CANCEL_BTN = "[data-test='cancel']"


@pytest.fixture
def checkout_page(cart_page: Page) -> Page:
    """Cart page with one item, navigated to checkout step one."""
    cart_page.locator("[data-test='checkout']").click()
    cart_page.wait_for_url(f"{BASE_URL}/checkout-step-one.html")
    return cart_page


# =============================================
# COMPLETE CHECKOUT FLOW
# =============================================

def test_complete_checkout_flow(cart_page: Page):
    """
    Full end-to-end checkout: cart -> info -> review -> complete.
    This is the most important test in the suite.
    It validates the entire happy path a real user takes.
    """
    # Step 1: Go to checkout
    cart_page.locator("[data-test='checkout']").click()
    expect(cart_page).to_have_url(f"{BASE_URL}/checkout-step-one.html")

    # Step 2: Fill in customer information
    cart_page.fill(FIRST_NAME, "Divya")
    cart_page.fill(LAST_NAME, "Kumar")
    cart_page.fill(POSTAL_CODE, "600001")
    cart_page.locator(CONTINUE_BTN).click()

    # Step 3: Verify order review page
    expect(cart_page).to_have_url(f"{BASE_URL}/checkout-step-two.html")
    expect(cart_page.locator(".cart_item")).to_have_count(1)
    expect(
        cart_page.locator(".inventory_item_name")
    ).to_have_text("Sauce Labs Backpack")

    # Step 4: Verify price summary is shown
    expect(cart_page.locator(".summary_subtotal_label")).to_be_visible()
    expect(cart_page.locator(".summary_tax_label")).to_be_visible()
    expect(cart_page.locator(".summary_total_label")).to_be_visible()

    # Step 5: Finish the order
    cart_page.locator(FINISH_BTN).click()

    # Step 6: Verify success
    expect(cart_page).to_have_url(f"{BASE_URL}/checkout-complete.html")
    expect(
        cart_page.locator("[data-test='complete-header']")
    ).to_have_text("Thank you for your order!")


def test_checkout_complete_page_has_back_home_button(cart_page: Page):
    cart_page.locator("[data-test='checkout']").click()
    cart_page.fill(FIRST_NAME, "Test")
    cart_page.fill(LAST_NAME, "User")
    cart_page.fill(POSTAL_CODE, "123456")
    cart_page.locator(CONTINUE_BTN).click()
    cart_page.locator(FINISH_BTN).click()

    expect(cart_page).to_have_url(f"{BASE_URL}/checkout-complete.html")

    back_btn = cart_page.locator("[data-test='back-to-products']")
    expect(back_btn).to_be_visible()
    back_btn.click()

    expect(cart_page).to_have_url(f"{BASE_URL}/inventory.html")


def test_order_summary_shows_correct_item(cart_page: Page):
    cart_page.locator("[data-test='checkout']").click()
    cart_page.fill(FIRST_NAME, "Arjun")
    cart_page.fill(LAST_NAME, "Sharma")
    cart_page.fill(POSTAL_CODE, "400001")
    cart_page.locator(CONTINUE_BTN).click()

    # Verify the item in the order summary
    item_name = cart_page.locator(".inventory_item_name").text_content()
    item_price = cart_page.locator(".inventory_item_price").text_content()

    assert "Sauce Labs Backpack" in item_name
    assert item_price.startswith("$")


def test_order_total_includes_tax(cart_page: Page):
    cart_page.locator("[data-test='checkout']").click()
    cart_page.fill(FIRST_NAME, "Test")
    cart_page.fill(LAST_NAME, "User")
    cart_page.fill(POSTAL_CODE, "600001")
    cart_page.locator(CONTINUE_BTN).click()

    subtotal_text = cart_page.locator(
        ".summary_subtotal_label"
    ).text_content()
    tax_text = cart_page.locator(".summary_tax_label").text_content()
    total_text = cart_page.locator(".summary_total_label").text_content()

    # Extract numbers
    subtotal = float(subtotal_text.split("$")[1])
    tax = float(tax_text.split("$")[1])
    total = float(total_text.split("$")[1])

    assert abs((subtotal + tax) - total) < 0.01, \
        f"Total {total} should equal subtotal {subtotal} + tax {tax}"


# =============================================
# VALIDATION ERRORS
# =============================================

def test_missing_first_name_shows_error(checkout_page: Page):
    checkout_page.fill(LAST_NAME, "Kumar")
    checkout_page.fill(POSTAL_CODE, "600001")
    checkout_page.locator(CONTINUE_BTN).click()

    expect(checkout_page.locator(ERROR_MSG)).to_be_visible()
    expect(checkout_page.locator(ERROR_MSG)).to_contain_text(
        "First Name is required"
    )


def test_missing_last_name_shows_error(checkout_page: Page):
    checkout_page.fill(FIRST_NAME, "Divya")
    checkout_page.fill(POSTAL_CODE, "600001")
    checkout_page.locator(CONTINUE_BTN).click()

    expect(checkout_page.locator(ERROR_MSG)).to_be_visible()
    expect(checkout_page.locator(ERROR_MSG)).to_contain_text(
        "Last Name is required"
    )


def test_missing_postal_code_shows_error(checkout_page: Page):
    checkout_page.fill(FIRST_NAME, "Divya")
    checkout_page.fill(LAST_NAME, "Kumar")
    checkout_page.locator(CONTINUE_BTN).click()

    expect(checkout_page.locator(ERROR_MSG)).to_be_visible()
    expect(checkout_page.locator(ERROR_MSG)).to_contain_text(
        "Postal Code is required"
    )


def test_all_fields_empty_shows_first_name_error(checkout_page: Page):
    checkout_page.locator(CONTINUE_BTN).click()

    expect(checkout_page.locator(ERROR_MSG)).to_contain_text(
        "First Name is required"
    )


def test_cancel_from_checkout_info_returns_to_cart(checkout_page: Page):
    checkout_page.locator(CANCEL_BTN).click()

    expect(checkout_page).to_have_url(f"{BASE_URL}/cart.html")


def test_cancel_from_order_review_returns_to_inventory(cart_page: Page):
    cart_page.locator("[data-test='checkout']").click()
    cart_page.fill(FIRST_NAME, "Test")
    cart_page.fill(LAST_NAME, "User")
    cart_page.fill(POSTAL_CODE, "12345")
    cart_page.locator(CONTINUE_BTN).click()

    expect(cart_page).to_have_url(f"{BASE_URL}/checkout-step-two.html")

    cart_page.locator(CANCEL_BTN).click()

    expect(cart_page).to_have_url(f"{BASE_URL}/inventory.html")