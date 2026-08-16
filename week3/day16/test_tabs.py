# week3/day16/test_tabs.py
# Multiple tabs and windows in Playwright
# Run with: pytest week3/day16/test_tabs.py -v -s

import pytest
from playwright.sync_api import Page, BrowserContext, expect

INTERNET_URL = "https://the-internet.herokuapp.com"
SAUCE_URL = "https://www.saucedemo.com"


def test_handle_new_tab_opened_by_link(context: BrowserContext):
    """
    When a link has target="_blank", clicking it opens a new tab.
    Playwright handles this with context.expect_page().

    The pattern:
    with context.expect_page() as new_page_info:
        click_the_link_that_opens_new_tab()
    new_page = new_page_info.value

    context.expect_page() listens for a new page event.
    When the click fires and opens a new tab, it captures it.
    new_page_info.value gives you the Page object for the new tab.
    """
    page = context.new_page()
    page.goto(f"{INTERNET_URL}/windows")

    print(f"\n  [TABS] Initial page: {page.url}")
    print(f"  [TABS] Open tabs before click: {len(context.pages)}")

    # expect_page() waits for a new page to open
    with context.expect_page() as new_page_info:
        page.get_by_role("link", name="Click Here").click()

    new_tab = new_page_info.value
    new_tab.wait_for_load_state()

    print(f"  [TABS] New tab URL: {new_tab.url}")
    print(f"  [TABS] Open tabs after click: {len(context.pages)}")

    # Verify the new tab loaded correctly
    assert "new_window" in new_tab.url or len(new_tab.url) > 0
    expect(new_tab.locator("h3")).to_be_visible()

    # Both tabs are accessible
    assert len(context.pages) == 2
    print(f"  [TABS] Original tab still on: {page.url}")
    print(f"  [TABS] New tab on: {new_tab.url}")
    
    
def test_interact_with_both_tabs(context: BrowserContext):
    """
    After a new tab opens, you can interact with BOTH tabs.
    Switch between them by using the respective Page objects.
    This simulates a real user workflow where they open something
    in a new tab, check it, then switch back.
    """
    page = context.new_page()
    page.goto(f"{INTERNET_URL}/windows")

    with context.expect_page() as new_page_info:
        page.get_by_role("link", name="Click Here").click()

    new_tab = new_page_info.value
    new_tab.wait_for_load_state()

    # Interact with new tab
    new_tab_title = new_tab.locator("h3").text_content()
    print(f"\n  [TABS] New tab h3: '{new_tab_title}'")

    # Switch back to original tab and interact with it
    original_heading = page.locator("h3").first.text_content()
    print(f"  [TABS] Original tab h3: '{original_heading}'")

    # Close the new tab
    new_tab.close()
    assert len(context.pages) == 1
    print(f"  [TABS] After closing new tab: {len(context.pages)} tab(s) open")


def test_get_all_open_tabs(context: BrowserContext):
    """
    context.pages returns a list of ALL open pages in this context.
    Use this to verify how many tabs are open,
    or to iterate over all tabs.
    """
    page = context.new_page()
    page.goto(f"{INTERNET_URL}/windows")

    assert len(context.pages) == 1

    # Open new tab
    with context.expect_page() as new_page_info:
        page.get_by_role("link", name="Click Here").click()

    new_tab = new_page_info.value
    new_tab.wait_for_load_state()

    all_pages = context.pages
    print(f"\n  [TABS] All open tabs ({len(all_pages)}):")
    for i, pg in enumerate(all_pages):
        print(f"    Tab {i + 1}: {pg.url}")

    assert len(all_pages) == 2


def test_popup_window(context: BrowserContext):
    """
    Some applications open popup windows (smaller browser windows).
    Playwright treats them the same as new tabs — both are Page objects.
    context.expect_page() catches both.
    """
    page = context.new_page()
    page.goto(f"{INTERNET_URL}/windows")

    # The new window link opens a new window
    with context.expect_page() as popup_info:
        page.locator("a[href='/windows/new']").click()

    popup = popup_info.value
    popup.wait_for_load_state()

    print(f"\n  [POPUP] Popup URL: {popup.url}")
    print(f"  [POPUP] Popup title: '{popup.title()}'")

    expect(popup).to_have_url(f"{INTERNET_URL}/windows/new")
    
    
def test_close_tab_and_continue_on_original(context: BrowserContext):
    """
    After handling a new tab, close it and continue working
    on the original tab. Verify the original tab is unaffected.
    """
    page = context.new_page()
    page.goto(f"{INTERNET_URL}/windows")

    original_url = page.url

    with context.expect_page() as new_page_info:
        page.get_by_role("link", name="Click Here").click()

    new_tab = new_page_info.value
    new_tab.wait_for_load_state()

    # Do something in the new tab
    print(f"\n  [TABS] New tab loaded: {new_tab.url}")

    # Close new tab
    new_tab.close()

    # Original tab is unaffected
    assert page.url == original_url
    assert len(context.pages) == 1
    expect(page.locator("h3").first).to_be_visible()

    print(f"  [TABS] Back on original: {page.url}")
    print(f"  [TABS] Original tab still functional")