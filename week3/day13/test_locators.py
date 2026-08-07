# week3/day13/test_locators.py
# Locator strategy practice against saucedemo.com
# Run with: pytest week3/day13/test_locators.py -v -s

import pytest
from playwright.sync_api import Page, expect, sync_playwright

BASE_URL = "https://www.saucedemo.com"
VALID_USER = "standard_user"
VALID_PASS = "secret_sauce"


# =============================================
# SHARED FIXTURES
# =============================================

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

@pytest.fixture(scope="function")
def page(browser):
    context = browser.new_context(viewport={"width": 1280, "height": 720})
    pg = context.new_page()
    pg.set_default_timeout(15_000)
    yield pg
    context.close()

@pytest.fixture(scope="function")
def login_page(page):
    page.goto(BASE_URL)
    return page

@pytest.fixture(scope="function")
def inventory_page(page):
    """Already logged in, on the inventory page."""
    page.goto(BASE_URL)
    page.fill("#user-name", VALID_USER)
    page.fill("#password", VALID_PASS)
    page.click("#login-button")
    expect(page).to_have_url(f"{BASE_URL}/inventory.html")
    return page


# =============================================
# SECTION 1: get_by_role
# =============================================
# Role-based locators find elements by what they ARE to a user.
# A button is a button. A heading is a heading. A textbox is a textbox.
# This is how screen readers see the page.
# Most resilient: survives CSS changes, class renames, DOM restructuring.

def test_role_login_button_is_clickable(login_page: Page):
    """
    Locate the login button by its role and name.
    Even if the class changes from .btn-action to .btn-primary,
    this locator still works because it finds by role=button + name.
    """
    login_page.fill("#user-name", VALID_USER)
    login_page.fill("#password", VALID_PASS)

    # get_by_role finds the element by its ARIA role and accessible name
    # The accessible name for a button is its visible text
    login_page.get_by_role("button", name="Login").click()

    expect(login_page).to_have_url(f"{BASE_URL}/inventory.html")
    print("\n  [ROLE] Found login button by role=button, name='Login'")


def test_role_heading_shows_products_after_login(inventory_page: Page):
    """
    Locate the page heading by its role.
    h1, h2, h3 all have role=heading.
    name= matches the visible text inside the heading.
    """
    heading = inventory_page.get_by_role("heading", name="Products")
    expect(heading).to_be_visible()
    print(f"\n  [ROLE] Found heading: '{heading.text_content()}'")


def test_role_link_to_navigate(inventory_page: Page):
    """
    Locate a link by its role.
    The cart icon is a link with role=link.
    """
    # The shopping cart link
    cart_link = inventory_page.get_by_role("link", name="shopping cart")
    # If exact name doesn't match, use contains approach
    # Let's try the cart badge area instead
    cart = inventory_page.locator(".shopping_cart_link")
    expect(cart).to_be_visible()
    print("\n  [ROLE] Cart link is visible on inventory page")


# =============================================
# SECTION 2: get_by_label
# =============================================
# Finds form inputs by their associated <label> text.
# Works when a <label for="input-id"> is present in the HTML.
# More semantic than CSS — describes the field's purpose not its implementation.
# saucedemo does not have proper <label> elements but has placeholder text.
# So we demonstrate get_by_label concept and fall back to get_by_placeholder.

def test_label_username_field(login_page: Page):
    """
    saucedemo uses placeholder text instead of label elements.
    get_by_placeholder finds inputs by their placeholder attribute.
    Same semantic benefit as get_by_label — describes purpose not implementation.

    What get_by_label would look like on a properly labelled form:
    page.get_by_label("Username").fill("standard_user")

    What we use here since saucedemo has no labels:
    page.get_by_placeholder("Username").fill("standard_user")
    """
    login_page.get_by_placeholder("Username").fill(VALID_USER)
    login_page.get_by_placeholder("Password").fill(VALID_PASS)
    login_page.get_by_role("button", name="Login").click()

    expect(login_page).to_have_url(f"{BASE_URL}/inventory.html")
    print("\n  [LABEL/PLACEHOLDER] Found fields by placeholder text")


def test_label_fill_username_only(login_page: Page):
    """
    Use placeholder to find username field specifically.
    Then assert error message when password is missing.
    """
    login_page.get_by_placeholder("Username").fill(VALID_USER)
    # Do not fill password
    login_page.get_by_role("button", name="Login").click()

    error = login_page.locator("[data-test='error']")
    expect(error).to_be_visible()
    expect(error).to_contain_text("Password is required")
    print(f"\n  [LABEL/PLACEHOLDER] Error: '{error.text_content().strip()}'")


def test_label_fill_password_only(login_page: Page):
    """
    Use placeholder to find password field specifically.
    Then assert error when username is missing.
    """
    login_page.get_by_placeholder("Password").fill(VALID_PASS)
    # Do not fill username
    login_page.get_by_role("button", name="Login").click()

    error = login_page.locator("[data-test='error']")
    expect(error).to_be_visible()
    expect(error).to_contain_text("Username is required")
    print(f"\n  [LABEL/PLACEHOLDER] Error: '{error.text_content().strip()}'")


# =============================================
# SECTION 3: CSS Selectors
# =============================================
# Finds elements by CSS class, ID, attribute, or structure.
# Fast and powerful — but brittle.
# A class rename from .btn-action to .btn-primary breaks everything.
# Use CSS when:
#   - The element has a stable ID (#user-name, #login-button)
#   - The app sets data-test attributes specifically for testing
#   - No semantic locator fits

def test_css_id_selector_login(login_page: Page):
    """
    ID selectors (#id) are the most stable CSS locators.
    IDs are meant to be unique and rarely change.
    This is why #user-name and #login-button are acceptable CSS locators.
    """
    login_page.locator("#user-name").fill(VALID_USER)
    login_page.locator("#password").fill(VALID_PASS)
    login_page.locator("#login-button").click()

    expect(login_page).to_have_url(f"{BASE_URL}/inventory.html")
    print("\n  [CSS ID] Found elements by #id selector")


def test_css_data_attribute_selector(login_page: Page):
    """
    data-test="attribute" selectors are the BEST CSS locators.
    They are added specifically for testing, not styling.
    A designer can rename every CSS class without breaking this.
    Modern apps set data-testid or data-test attributes for this reason.
    """
    # saucedemo sets data-test attributes on error message
    login_page.locator("#user-name").fill("wrong_user")
    login_page.locator("#password").fill("wrong_pass")
    login_page.locator("#login-button").click()

    # [data-test='error'] is a CSS attribute selector
    # It says: find any element with a data-test attribute equal to 'error'
    error = login_page.locator("[data-test='error']")
    expect(error).to_be_visible()
    expect(error).to_contain_text("Username and password do not match")
    print(f"\n  [CSS DATA-ATTR] Found error by [data-test='error']")


def test_css_class_selector_inventory_items(inventory_page: Page):
    """
    Class selectors (.classname) are the most brittle CSS locators.
    If the developer renames .inventory_item to .product-card,
    this test breaks immediately even though the page looks identical.

    Use class selectors only when:
    - No ID or data attribute is available
    - The class name is semantically meaningful (not utility CSS)
    - You accept the maintenance cost
    """
    items = inventory_page.locator(".inventory_item")
    item_count = items.count()

    assert item_count == 6, f"Expected 6 items, got {item_count}"
    print(f"\n  [CSS CLASS] Found {item_count} .inventory_item elements")

    # Get first item's name
    first_item_name = inventory_page.locator(".inventory_item_name").first
    name_text = first_item_name.text_content()
    print(f"  [CSS CLASS] First item: '{name_text}'")


# =============================================
# SECTION 4: The Comparison Test
# =============================================
# This test demonstrates all three strategies on the SAME action.
# Shows you exactly what each looks like side by side.

def test_three_strategies_same_action(login_page: Page):
    """
    Three ways to find the username input field.
    All three work. They differ in resilience.

    Resilience ranking for username field:
    1. get_by_placeholder("Username") - survives class/id changes
    2. locator("#user-name")          - survives class changes, breaks on id change
    3. locator(".input_error")        - breaks on any class rename
    """

    # Strategy 1: by placeholder (best for form inputs without labels)
    login_page.get_by_placeholder("Username").fill(VALID_USER)
    login_page.get_by_placeholder("Username").clear()

    # Strategy 2: by ID (stable if IDs don't change)
    login_page.locator("#user-name").fill(VALID_USER)
    login_page.locator("#user-name").clear()

    # Strategy 3: by CSS class (most brittle - avoid)
    login_page.locator(".form_input").first.fill(VALID_USER)

    # Complete login with the most resilient strategy
    login_page.get_by_placeholder("Password").fill(VALID_PASS)
    login_page.get_by_role("button", name="Login").click()

    expect(login_page).to_have_url(f"{BASE_URL}/inventory.html")
    print("\n  [COMPARISON] All three strategies found the same element")
    print("  Placeholder > ID > CSS Class (resilience order)")