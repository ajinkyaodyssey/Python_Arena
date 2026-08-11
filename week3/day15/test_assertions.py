# week3/day15/test_assertions.py
# Complete coverage of Playwright expect() assertions
# Every assertion type with at least 2 real tests
# Run with: pytest week3/day15/test_assertions.py -v -s

import pytest
import re
from playwright.sync_api import Page, expect

SAUCE_URL = "https://www.saucedemo.com"
INTERNET_URL = "https://the-internet.herokuapp.com"


# =============================================
# SECTION 1: URL Assertions
# =============================================
# expect(page).to_have_url() — checks the browser's current URL
# Critical for navigation tests — confirms the right page loaded

def test_url_exact_match_after_login(login_page: Page):
    """
    to_have_url() with exact string.
    Use when you know the exact URL the page should land on.
    Auto-retries until the URL matches or timeout expires —
    so you do not need an explicit wait for navigation.
    """
    login_page.fill("#user-name", "standard_user")
    login_page.fill("#password", "secret_sauce")
    login_page.click("#login-button")

    # No wait_for_url needed — expect() polls until it matches
    expect(login_page).to_have_url(f"{SAUCE_URL}/inventory.html")
    print(f"\n  [URL] Current URL: {login_page.url}")


def test_url_regex_match(login_page: Page):
    """
    to_have_url() with a regex pattern.
    Use when the URL has dynamic parts (query params, IDs)
    that you cannot predict exactly.
    re.compile() creates the pattern.
    """
    login_page.fill("#user-name", "standard_user")
    login_page.fill("#password", "secret_sauce")
    login_page.click("#login-button")

    # Regex: URL must contain 'inventory' anywhere
    expect(login_page).to_have_url(re.compile(r"inventory"))
    print(f"\n  [URL REGEX] URL matched pattern 'inventory': {login_page.url}")


def test_url_stays_on_login_page_after_invalid_credentials(login_page: Page):
    """
    Negative URL assertion — page should NOT navigate away.
    After a failed login the URL must remain on the login page.
    """
    login_page.fill("#user-name", "wrong_user")
    login_page.fill("#password", "wrong_pass")
    login_page.click("#login-button")

    # Should still be on the root login URL
    expect(login_page).to_have_url(f"{SAUCE_URL}/")
    print(f"\n  [URL] Stayed on login page after failure: {login_page.url}")


# =============================================
# SECTION 2: Title Assertions
# =============================================

def test_page_title_on_login_page(login_page: Page):
    """
    to_have_title() checks the browser tab title (the <title> HTML tag).
    Different from the visible heading on the page.
    """
    expect(login_page).to_have_title("Swag Labs")
    print(f"\n  [TITLE] Page title: '{login_page.title()}'")


def test_page_title_regex(login_page: Page):
    """
    to_have_title() also accepts regex.
    """
    expect(login_page).to_have_title(re.compile(r"Swag", re.IGNORECASE))
    print(f"\n  [TITLE REGEX] Title matched 'Swag': '{login_page.title()}'")


# =============================================
# SECTION 3: Visibility Assertions
# =============================================
# to_be_visible() — element exists in DOM AND is visible to user
# to_be_hidden()  — element either not in DOM OR in DOM but invisible
# These are the most used assertions in UI testing

def test_error_message_visible_after_bad_login(login_page: Page):
    """
    to_be_visible() waits until the element is:
    1. Attached to the DOM
    2. Not hidden (display not none, visibility not hidden)
    3. Not covered by another element
    4. Has non-zero size
    All four conditions must be true.
    """
    login_page.fill("#user-name", "wrong_user")
    login_page.fill("#password", "wrong_pass")
    login_page.click("#login-button")

    error = login_page.locator("[data-test='error']")
    expect(error).to_be_visible()
    print(f"\n  [VISIBLE] Error is visible: '{error.text_content().strip()}'")


def test_error_message_not_visible_on_fresh_login_page(login_page: Page):
    """
    not_to_be_visible() is the negative assertion.
    On a fresh login page there should be no error showing.
    """
    error = login_page.locator("[data-test='error']")
    expect(error).not_to_be_visible()
    print("\n  [HIDDEN] Error correctly hidden on fresh page")


def test_inventory_items_visible_after_login(inventory_page: Page):
    """
    Check that product items appear after login.
    to_be_visible() on the first item confirms the page loaded correctly.
    """
    first_item = inventory_page.locator(".inventory_item").first
    expect(first_item).to_be_visible()
    print("\n  [VISIBLE] First inventory item is visible after login")


def test_cart_badge_hidden_when_cart_empty(inventory_page: Page):
    """
    Cart badge should not show when nothing is in the cart.
    """
    badge = inventory_page.locator(".shopping_cart_badge")
    expect(badge).not_to_be_visible()
    print("\n  [HIDDEN] Cart badge correctly hidden when cart empty")


def test_cart_badge_visible_after_adding_item(inventory_page: Page):
    """
    Cart badge appears after adding an item.
    Demonstrates visibility changing as a result of an action.
    """
    badge = inventory_page.locator(".shopping_cart_badge")
    expect(badge).not_to_be_visible()

    inventory_page.locator(
        "[data-test='add-to-cart-sauce-labs-backpack']"
    ).click()

    expect(badge).to_be_visible()
    print(f"\n  [VISIBLE] Badge appeared after add to cart: '{badge.text_content()}'")


# =============================================
# SECTION 4: Text Content Assertions
# =============================================
# to_have_text()     — full exact text match
# to_contain_text()  — partial text match (substring)
# Use to_contain_text() when you only care about part of the text
# Use to_have_text() when you need exact match

def test_have_text_exact_match(inventory_page: Page):
    """
    to_have_text() matches the FULL text of the element.
    Whitespace is normalised — leading/trailing spaces ignored.
    If element has "  Products  ", to_have_text("Products") passes.
    """
    heading = inventory_page.locator(".title")
    expect(heading).to_have_text("Products")
    print(f"\n  [TEXT EXACT] Heading text: '{heading.text_content()}'")


def test_have_text_on_add_to_cart_button(inventory_page: Page):
    """
    Verify a specific button has the correct label.
    """
    add_btn = inventory_page.locator(
        "[data-test='add-to-cart-sauce-labs-backpack']"
    )
    expect(add_btn).to_have_text("Add to cart")
    print(f"\n  [TEXT EXACT] Button text: '{add_btn.text_content()}'")


def test_contain_text_partial_match_on_error(login_page: Page):
    """
    to_contain_text() checks if the text CONTAINS the substring.
    More flexible than to_have_text() for long error messages.
    """
    login_page.fill("#user-name", "locked_out_user")
    login_page.fill("#password", "secret_sauce")
    login_page.click("#login-button")

    error = login_page.locator("[data-test='error']")
    # Only check for the meaningful part, not the full "Epic sadface:" prefix
    expect(error).to_contain_text("locked out")
    print(f"\n  [CONTAIN TEXT] Error contains 'locked out': '{error.text_content().strip()}'")


def test_contain_text_regex_pattern(inventory_page: Page):
    """
    to_contain_text() also accepts regex for flexible matching.
    Useful when the exact wording might vary but the pattern is fixed.
    """
    price = inventory_page.locator(".inventory_item_price").first
    # Price should match pattern like $XX.XX
    expect(price).to_contain_text(re.compile(r"\$\d+\.\d{2}"))
    print(f"\n  [CONTAIN REGEX] Price matches dollar pattern: '{price.text_content()}'")


def test_button_text_changes_after_add_to_cart(inventory_page: Page):
    """
    After clicking Add to cart, the button text changes to Remove.
    to_have_text() confirms the DOM updated correctly.
    """
    add_btn = inventory_page.locator(
        "[data-test='add-to-cart-sauce-labs-backpack']"
    )
    expect(add_btn).to_have_text("Add to cart")

    add_btn.click()

    remove_btn = inventory_page.locator(
        "[data-test='remove-sauce-labs-backpack']"
    )
    expect(remove_btn).to_have_text("Remove")
    print("\n  [TEXT] Button text changed from 'Add to cart' to 'Remove'")


# =============================================
# SECTION 5: Count Assertions
# =============================================
# to_have_count() — verifies exactly how many elements match a locator

def test_inventory_has_six_items(inventory_page: Page):
    """
    to_have_count() verifies the exact number of matching elements.
    Useful for: checking paginated results, verifying filters work,
    confirming all expected items rendered.
    """
    items = inventory_page.locator(".inventory_item")
    expect(items).to_have_count(6)
    print(f"\n  [COUNT] Inventory item count: {items.count()}")


def test_cart_count_increments_correctly(inventory_page: Page):
    """
    Add two items and verify cart count assertion.
    """
    badge = inventory_page.locator(".shopping_cart_badge")
    expect(badge).not_to_be_visible()

    inventory_page.locator(
        "[data-test='add-to-cart-sauce-labs-backpack']"
    ).click()
    expect(badge).to_have_text("1")

    inventory_page.locator(
        "[data-test='add-to-cart-sauce-labs-bike-light']"
    ).click()
    expect(badge).to_have_text("2")
    print(f"\n  [COUNT] Badge correctly shows 2 after adding 2 items")


def test_filter_reduces_visible_items(inventory_page: Page):
    """
    After sorting, all 6 items should still be present.
    count() confirms filtering did not accidentally hide items.
    """
    sort_dropdown = inventory_page.locator(
        "[data-test='product-sort-container']"
    )
    sort_dropdown.select_option(value="za")

    items = inventory_page.locator(".inventory_item_name")
    expect(items).to_have_count(6)

    all_names = items.all_text_contents()
    print(f"\n  [COUNT] After Z-A sort, still {len(all_names)} items")
    print(f"  First item: '{all_names[0]}'")


# =============================================
# SECTION 6: State Assertions
# =============================================
# to_be_enabled()  — element can be interacted with
# to_be_disabled() — element cannot be interacted with
# to_be_checked()  — checkbox/radio is ticked
# to_be_editable() — input can be typed in

def test_login_button_is_enabled(login_page: Page):
    """
    to_be_enabled() checks that an element does not have
    the disabled attribute. Important for form validation tests
    where submit buttons should only be active when form is valid.
    """
    login_btn = login_page.locator("#login-button")
    expect(login_btn).to_be_enabled()
    print("\n  [ENABLED] Login button is enabled")


def test_checkbox_checked_state(page: Page):
    """
    to_be_checked() verifies a checkbox is in checked state.
    Cleaner than: assert checkbox.is_checked() == True
    because it auto-retries.
    """
    page.goto(f"{INTERNET_URL}/checkboxes")
    checkboxes = page.locator("input[type='checkbox']")

    # Check the first checkbox
    checkboxes.nth(0).check()
    expect(checkboxes.nth(0)).to_be_checked()
    print("\n  [CHECKED] First checkbox is checked")

    # Uncheck it
    checkboxes.nth(0).uncheck()
    expect(checkboxes.nth(0)).not_to_be_checked()
    print("  [UNCHECKED] First checkbox is now unchecked")


def test_input_is_editable(login_page: Page):
    """
    to_be_editable() checks the input is not readonly or disabled.
    """
    username_input = login_page.locator("#user-name")
    password_input = login_page.locator("#password")

    expect(username_input).to_be_editable()
    expect(password_input).to_be_editable()
    print("\n  [EDITABLE] Both inputs are editable")


# =============================================
# SECTION 7: Attribute Assertions
# =============================================
# to_have_attribute() — checks an element's HTML attribute value
# to_have_value()     — checks the current value of an input

def test_have_attribute_on_input(login_page: Page):
    """
    to_have_attribute() checks an element has a specific attribute
    with a specific value. Useful for ARIA attributes, data attributes,
    type attributes.
    """
    username_input = login_page.locator("#user-name")

    # Check the type attribute
    expect(username_input).to_have_attribute("type", "text")
    print("\n  [ATTR] Username input has type='text'")

    # Check placeholder attribute
    expect(username_input).to_have_attribute("placeholder", "Username")
    print("  [ATTR] Username input has placeholder='Username'")


def test_have_attribute_data_test(login_page: Page):
    """
    Verify data-test attributes exist on elements.
    This confirms the app is set up correctly for test automation.
    Missing data-test attributes should be raised as issues
    with the development team.
    """
    login_page.fill("#user-name", "wrong")
    login_page.fill("#password", "wrong")
    login_page.click("#login-button")

    error = login_page.locator("[data-test='error']")
    expect(error).to_have_attribute("data-test", "error")
    print("\n  [ATTR] Error element has correct data-test attribute")


def test_have_value_in_input(login_page: Page):
    """
    to_have_value() checks the current value of an input field.
    Different from to_have_text() which checks visible text.
    Input elements display their value but text_content() returns empty.
    """
    login_page.fill("#user-name", "standard_user")

    username_input = login_page.locator("#user-name")
    expect(username_input).to_have_value("standard_user")
    print("\n  [VALUE] Input value is 'standard_user'")


def test_have_value_changes_after_fill(login_page: Page):
    """
    Confirm value updates correctly after each fill().
    """
    username_input = login_page.locator("#user-name")

    login_page.fill("#user-name", "first_user")
    expect(username_input).to_have_value("first_user")

    login_page.fill("#user-name", "second_user")
    expect(username_input).to_have_value("second_user")
    print("\n  [VALUE] Value correctly updated after second fill()")


# =============================================
# SECTION 8: CSS Class Assertion
# =============================================

def test_have_class_on_error_button(login_page: Page):
    """
    to_have_class() checks that an element has a specific CSS class.
    Useful when your test needs to verify visual state changes
    that are implemented via class toggling.
    """
    login_page.fill("#user-name", "wrong")
    login_page.fill("#password", "wrong")
    login_page.click("#login-button")

    error_container = login_page.locator(".error-message-container")

    expect(error_container).to_be_visible()
    expect(error_container).to_have_class(re.compile(r".*\berror\b.*"))

    print("\n  [CLASS] Error container has class 'error'")


# =============================================
# SECTION 9: Soft Assertions (expect.soft)
# =============================================
# Regular assertions stop the test on first failure.
# Soft assertions continue running even after a failure.
# At the end of the test, ALL failures are reported together.
# Use when you want to check multiple things and see ALL failures.

def test_soft_assertions_report_all_failures(inventory_page: Page):
    """
    expect.soft() continues past failures.
    Regular expect() stops at the first one.

    Use case: validating a product listing page where you want
    to see ALL wrong fields at once rather than fixing one,
    re-running, finding the next, etc.
    """
    first_item_name = inventory_page.locator(".inventory_item_name").first
    first_item_price = inventory_page.locator(".inventory_item_price").first
    cart_badge = inventory_page.locator(".shopping_cart_badge")

    expect.soft(first_item_name).to_be_visible()
    expect.soft(first_item_price).to_be_visible()
    expect.soft(cart_badge).not_to_be_visible()
    expect.soft(
        inventory_page.locator(".title")
    ).to_have_text("Products")

    print("\n  [SOFT] All soft assertions checked")


# =============================================
# SECTION 10: The Assertion Cheat Sheet Test
# =============================================
# One test that demonstrates every assertion type
# in context. Use as a quick reference.

def test_assertion_reference_card(inventory_page: Page):
    """
    Quick reference for all expect() assertions.
    Run this test with -s to see all output.
    """
    page = inventory_page

    # --- PAGE LEVEL ---
    expect(page).to_have_url(f"{SAUCE_URL}/inventory.html")
    expect(page).to_have_title("Swag Labs")

    # --- VISIBILITY ---
    expect(page.locator(".inventory_list")).to_be_visible()
    expect(page.locator(".shopping_cart_badge")).not_to_be_visible()

    # --- TEXT ---
    expect(page.locator(".title")).to_have_text("Products")
    expect(page.locator(".inventory_item_price").first).to_contain_text("$")

    # --- COUNT ---
    expect(page.locator(".inventory_item")).to_have_count(6)

    # --- STATE ---
    expect(page.locator("#react-burger-menu-btn")).to_be_enabled()
    expect(page.locator("#react-burger-menu-btn")).to_be_visible()

    # --- ATTRIBUTE ---
    expect(
        page.locator("[data-test='product-sort-container']")
    ).to_have_attribute(
        "class",
        re.compile(r"product_sort_container")
    )

    # --- VALUE ---
    sort = page.locator("[data-test='product-sort-container']")
    expect(sort).to_have_value("az")    # default sort is A-Z

    print("\n  [REFERENCE] All assertion types demonstrated")
    print(f"  URL: {page.url}")
    print(f"  Title: {page.title()}")