# week3/day14/test_actions.py
# Playwright action tests: click, fill, check, uncheck,
# select_option, hover, keyboard, file upload
# Run with: pytest week3/day14/test_actions.py -v -s

import pytest
import os
from playwright.sync_api import Page, expect

SAUCE_URL = "https://www.saucedemo.com"
INTERNET_URL = "https://the-internet.herokuapp.com"


# =============================================
# SECTION 1: click() and fill()
# =============================================
# You already know these from Day 12.
# Today we go deeper: double click, right click,
# click with modifiers, clearing fields.

def test_fill_clears_existing_content(sauce_login: Page):
    """
    fill() REPLACES whatever is in the field.
    It does not append. It clears first then types.
    Use fill() almost always.
    Use press_sequentially() only for apps that react to keystrokes
    (autocomplete dropdowns, character-by-character validators).
    """
    # Go to a page with an input - use the search on inventory
    # saucedemo doesn't have search, so let's go back to login page
    sauce_login.goto(SAUCE_URL)

    sauce_login.fill("#user-name", "first_value")
    value_after_first = sauce_login.locator("#user-name").input_value()
    assert value_after_first == "first_value"

    # fill() replaces - does not append
    sauce_login.fill("#user-name", "second_value")
    value_after_second = sauce_login.locator("#user-name").input_value()
    assert value_after_second == "second_value"
    assert "first_value" not in value_after_second

    print(f"\n  [FILL] After second fill: '{value_after_second}'")


def test_click_add_to_cart_updates_badge(sauce_login: Page):
    """
    Clicking Add to Cart should increment the cart badge counter.
    This tests that click() triggers the correct DOM update.
    """
    # Cart badge should not exist yet
    badge = sauce_login.locator(".shopping_cart_badge")
    assert not badge.is_visible(), "Cart should be empty at start"

    # Click Add to cart on first item
    sauce_login.locator(
        "[data-test='add-to-cart-sauce-labs-backpack']"
    ).click()

    # Badge should now show 1
    expect(badge).to_be_visible()
    expect(badge).to_have_text("1")
    print(f"\n  [CLICK] Cart badge after adding item: '{badge.text_content()}'")


def test_double_click(page: Page):
    """
    Explicitly select all text then replace with new value.
    dblclick() behaviour varies by OS and browser —
    it selects a word but not guaranteed to select all.
    Ctrl+A is the reliable way to select everything.
    """
    page.goto(f"{INTERNET_URL}/inputs")
    number_input = page.locator("input[type='number']")

    number_input.fill("42")

    # Select all then type - reliable cross-platform
    number_input.click()
    page.keyboard.press("Control+a")
    page.keyboard.type("99")

    value = number_input.input_value()
    assert value == "99", f"Expected 99 after select all + type, got {value}"
    print(f"\n  [KEYBOARD] Value after Ctrl+A + type: '{value}'")


# =============================================
# SECTION 2: check() and uncheck()
# =============================================

def test_check_checkbox(page: Page):
    """
    check() ticks a checkbox.
    It is smarter than click() for checkboxes:
    - check() only clicks if the box is currently unchecked
    - uncheck() only clicks if the box is currently checked
    - This prevents accidental toggling
    """
    page.goto(f"{INTERNET_URL}/checkboxes")

    checkboxes = page.locator("input[type='checkbox']")
    count = checkboxes.count()
    print(f"\n  [CHECK] Found {count} checkboxes")

    checkbox_1 = checkboxes.nth(0)   # first checkbox
    checkbox_2 = checkboxes.nth(1)   # second checkbox

    # Read initial state
    initial_1 = checkbox_1.is_checked()
    initial_2 = checkbox_2.is_checked()
    print(f"  [CHECK] Initial state: checkbox1={initial_1}, checkbox2={initial_2}")

    # Check both
    checkbox_1.check()
    checkbox_2.check()

    assert checkbox_1.is_checked() == True
    assert checkbox_2.is_checked() == True
    print("  [CHECK] Both checkboxes checked")


def test_uncheck_checkbox(page: Page):
    """
    uncheck() removes the tick from a checkbox.
    """
    page.goto(f"{INTERNET_URL}/checkboxes")

    checkboxes = page.locator("input[type='checkbox']")
    checkbox_2 = checkboxes.nth(1)   # second checkbox starts checked

    # Confirm it starts checked
    checkbox_2.check()   # ensure it is checked first
    assert checkbox_2.is_checked() == True

    # Uncheck it
    checkbox_2.uncheck()
    assert checkbox_2.is_checked() == False
    print(f"\n  [UNCHECK] checkbox2 is now: {checkbox_2.is_checked()}")


def test_check_is_idempotent(page: Page):
    """
    check() called on an already-checked box does nothing.
    This is why check() is safer than click() for checkboxes.
    click() on a checked box would uncheck it — wrong behaviour.
    """
    page.goto(f"{INTERNET_URL}/checkboxes")

    checkboxes = page.locator("input[type='checkbox']")
    checkbox = checkboxes.nth(1)   # starts checked

    # Call check() twice - should still be checked, not toggled off
    checkbox.check()
    checkbox.check()   # calling again should be safe

    assert checkbox.is_checked() == True
    print("\n  [CHECK] check() is idempotent - calling twice is safe")


# =============================================
# SECTION 3: select_option()
# =============================================

def test_select_option_by_value(page: Page):
    """
    select_option() works on <select> HTML elements (dropdowns).
    You can select by: value, label (visible text), or index.
    """
    page.goto(f"{INTERNET_URL}/dropdown")

    dropdown = page.locator("#dropdown")

    # Select by value attribute
    dropdown.select_option(value="1")
    selected = dropdown.input_value()
    print(f"\n  [SELECT] Selected by value '1': '{selected}'")
    assert selected == "1"


def test_select_option_by_label(page: Page):
    """
    Select by visible text (label).
    This is the most readable approach — matches what users see.
    """
    page.goto(f"{INTERNET_URL}/dropdown")

    dropdown = page.locator("#dropdown")

    # Select by the text the user sees
    dropdown.select_option(label="Option 2")
    selected = dropdown.input_value()
    print(f"\n  [SELECT] Selected by label 'Option 2': value='{selected}'")
    assert selected == "2"


def test_select_option_sort_on_saucedemo(sauce_login: Page):
    """
    Real-world select_option usage:
    The sort dropdown on saucedemo inventory page.
    """
    sort_dropdown = sauce_login.locator("[data-test='product-sort-container']")

    # Default sort
    default_value = sort_dropdown.input_value()
    print(f"\n  [SELECT] Default sort: '{default_value}'")

    # Select price high to low
    sort_dropdown.select_option(value="hilo")
    new_value = sort_dropdown.input_value()
    assert new_value == "hilo"
    print(f"  [SELECT] After sort change: '{new_value}'")

    # Verify items are now sorted by price (first item should be most expensive)
    prices = sauce_login.locator(".inventory_item_price").all_text_contents()
    print(f"  [SELECT] Prices after sort: {prices[:3]}")

    # Convert prices to floats and verify descending order
    price_values = [float(p.replace("$", "")) for p in prices]
    assert price_values == sorted(price_values, reverse=True), \
        "Prices should be in descending order after hilo sort"


# =============================================
# SECTION 4: hover()
# =============================================

def test_hover_reveals_hidden_content(page: Page):
    """
    hover() moves the mouse over an element.
    Many UIs show tooltips, menus, or hidden buttons on hover.
    Playwright's hover() triggers CSS :hover state.
    """
    page.goto(f"{INTERNET_URL}/hovers")

    # Three profile figures on this page
    figures = page.locator(".figure")
    figure_count = figures.count()
    print(f"\n  [HOVER] Found {figure_count} figure elements")

    # Before hover, the caption (with name) is hidden
    first_figure = figures.nth(0)
    caption = first_figure.locator(".figcaption")

    # Hover over the first figure
    first_figure.hover()

    # Caption should now be visible
    expect(caption).to_be_visible()
    caption_text = caption.text_content()
    print(f"  [HOVER] Caption revealed: '{caption_text.strip()}'")
    assert "user" in caption_text.lower() or "name" in caption_text.lower() \
        or len(caption_text.strip()) > 0


def test_hover_on_saucedemo_menu(sauce_login: Page):
    """
    The burger menu on saucedemo.
    Click to open, verify menu items appear.
    """
    # Open burger menu
    sauce_login.locator("#react-burger-menu-btn").click()

    # Menu items should become visible
    menu = sauce_login.locator(".bm-menu-wrap")
    expect(menu).to_be_visible()

    logout_link = sauce_login.locator("#logout_sidebar_link")
    expect(logout_link).to_be_visible()
    print(f"\n  [HOVER/CLICK] Menu opened, logout link visible")


# =============================================
# SECTION 5: Keyboard actions
# =============================================

def test_keyboard_press_enter_to_submit(page: Page):
    """
    press() sends a keyboard key.
    Pressing Enter in a login form often submits it.
    """
    page.goto(SAUCE_URL)

    page.fill("#user-name", "standard_user")
    page.fill("#password", "secret_sauce")

    # Press Enter instead of clicking the button
    page.press("#password", "Enter")

    expect(page).to_have_url(f"{SAUCE_URL}/inventory.html")
    print("\n  [KEYBOARD] Enter key submitted the login form")


def test_keyboard_tab_navigation(page: Page):
    """
    Tab key moves focus between form fields.
    Important for accessibility testing.
    """
    page.goto(SAUCE_URL)

    # Click username field to focus it
    page.click("#user-name")
    page.keyboard.type("standard_user")

    # Tab to next field (password)
    page.keyboard.press("Tab")
    page.keyboard.type("secret_sauce")

    # Tab to login button and press Enter
    page.keyboard.press("Tab")
    page.keyboard.press("Enter")

    expect(page).to_have_url(f"{SAUCE_URL}/inventory.html")
    print("\n  [KEYBOARD] Tab navigation through login form worked")


# =============================================
# SECTION 6: File Upload
# =============================================

def test_file_upload_single_file(page: Page):
    """
    set_input_files() uploads a file to an <input type='file'> element.
    Playwright bypasses the OS file picker dialog entirely —
    it sets the files directly on the input element.
    This is why file upload tests are reliable in Playwright
    but were notoriously difficult in Selenium (OS dialogs are outside
    the browser and require separate tools to handle).
    """
    page.goto(f"{INTERNET_URL}/upload")

    # Create a temp file to upload
    test_file_path = "/tmp/test_upload.txt"
    with open(test_file_path, "w") as f:
        f.write("This is a test file for upload testing.\n")
        f.write("Content does not matter — we are testing the upload mechanism.")

    # Upload the file - no OS dialog appears
    file_input = page.locator("#file-upload")
    file_input.set_input_files(test_file_path)

    # Verify file name appears in the input
    # (browser shows selected file name)
    page.locator("#file-submit").click()

    # After upload, page should show success
    success = page.locator("#uploaded-files")
    expect(success).to_be_visible()
    uploaded_name = success.text_content().strip()
    assert "test_upload.txt" in uploaded_name
    print(f"\n  [UPLOAD] Successfully uploaded: '{uploaded_name}'")

    # Cleanup
    os.remove(test_file_path)


def test_file_upload_verifies_filename_before_submit(page: Page):
    """
    After set_input_files(), verify the correct file is selected
    BEFORE submitting. This catches wrong file selection bugs.
    """
    page.goto(f"{INTERNET_URL}/upload")

    test_file_path = "/tmp/test_data.csv"
    with open(test_file_path, "w") as f:
        f.write("id,name,status\n1,login_test,PASS\n2,checkout_test,FAIL\n")

    file_input = page.locator("#file-upload")
    file_input.set_input_files(test_file_path)

    # Check that the correct filename is shown
    # The input element's value contains the file path/name
    chosen_file = page.locator("#file-upload").input_value()
    print(f"\n  [UPLOAD] File selected: '{chosen_file}'")
    assert "test_data.csv" in chosen_file

    # Now submit
    page.locator("#file-submit").click()
    success = page.locator("#uploaded-files")
    expect(success).to_be_visible()

    os.remove(test_file_path)


# =============================================
# SECTION 7: Getting values from elements
# =============================================

def test_get_text_content(sauce_login: Page):
    """
    Different ways to read content from elements.
    Know the difference — they behave differently on different elements.
    """
    # text_content() - gets ALL text including hidden text
    first_item = sauce_login.locator(".inventory_item_name").first
    name = first_item.text_content()
    print(f"\n  [GET] text_content(): '{name}'")
    assert len(name) > 0

    # inner_text() - gets only VISIBLE text (respects CSS display:none)
    inner = first_item.inner_text()
    print(f"  [GET] inner_text(): '{inner}'")

    # input_value() - gets value of input/select/textarea
    sauce_login.goto(SAUCE_URL)
    username_input = sauce_login.locator("#user-name")
    sauce_login.fill("#user-name", "test_reading")
    value = username_input.input_value()
    print(f"  [GET] input_value(): '{value}'")
    assert value == "test_reading"


def test_get_attribute(sauce_login: Page):
    """
    get_attribute() reads an HTML attribute from an element.
    Useful for checking href, src, data-*, aria-* attributes.
    """
    # Get the data-test attribute of an add to cart button
    add_btn = sauce_login.locator(
        "[data-test='add-to-cart-sauce-labs-backpack']"
    )
    data_test_value = add_btn.get_attribute("data-test")
    print(f"\n  [ATTR] data-test value: '{data_test_value}'")
    assert "add-to-cart" in data_test_value

    # Get id attribute
    btn_id = add_btn.get_attribute("id")
    print(f"  [ATTR] id value: '{btn_id}'")


def test_get_all_items_count_and_names(sauce_login: Page):
    """
    all_text_contents() returns a list of text from all matching elements.
    count() returns how many elements match the locator.
    """
    items = sauce_login.locator(".inventory_item_name")
    count = items.count()
    all_names = items.all_text_contents()

    print(f"\n  [COUNT] Found {count} inventory items")
    print(f"  [ALL] Item names: {all_names}")

    assert count == 6, f"Expected 6 items, got {count}"
    assert len(all_names) == 6
    assert "Sauce Labs Backpack" in all_names