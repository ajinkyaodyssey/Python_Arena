# week4/day20/test_reporting_demo.py
# Demonstrates: HTML report, screenshot on failure, logging
# Run with: pytest week4/day20/ -v
# Then open: reports/report.html in your browser

import pytest
import logging
from playwright.sync_api import Page, expect

log = logging.getLogger(__name__)

BASE_URL = "https://www.saucedemo.com"


@pytest.fixture(scope="function")
def login_page(page: Page) -> Page:
    page.set_default_timeout(15_000)
    page.goto(BASE_URL)
    return page


# =============================================
# PASSING TEST — shows green in HTML report
# =============================================

def test_login_success_appears_green_in_report(login_page: Page):
    """
    This test passes.
    In the HTML report it shows as green with timing info.
    """
    log.info("Starting: test_login_success_appears_green_in_report")
    log.info(f"Navigated to: {login_page.url}")

    login_page.fill("#user-name", "standard_user")
    log.info("Filled username: standard_user")

    login_page.fill("#password", "secret_sauce")
    log.info("Filled password: [REDACTED]")

    login_page.click("#login-button")
    log.info("Clicked login button")

    expect(login_page).to_have_url(f"{BASE_URL}/inventory.html")
    log.info("Assertion passed: URL is inventory page")

    log.info("Test complete: PASS")


# =============================================
# FAILING TEST — shows red WITH screenshot
# =============================================

def test_login_failure_appears_red_with_screenshot(login_page: Page):
    """
    This test DELIBERATELY FAILS to demonstrate:
    1. Red entry in HTML report
    2. Automatic screenshot captured at failure moment
    3. Screenshot embedded in the HTML report
    4. Log trace showing exactly where it failed

    The screenshot shows what the browser looked like
    at the exact moment the assertion failed.
    This is how you debug CI failures without being there.
    """
    log.info("Starting: test_login_failure_appears_red_with_screenshot")

    login_page.fill("#user-name", "standard_user")
    log.info("Filled username: standard_user")

    login_page.fill("#password", "secret_sauce")
    log.info("Filled password: [REDACTED]")

    login_page.click("#login-button")
    log.info("Clicked login button")

    log.info("About to make a WRONG assertion to trigger failure")
    # Wrong assertion — deliberately fails
    expect(login_page).to_have_url(
        f"{BASE_URL}/wrong-page.html",
        timeout=3_000
    )
    # Screenshot is taken automatically by the hook in conftest
    # Open reports/report.html to see it embedded


# =============================================
# LOGGING LEVELS DEMO
# =============================================

def test_logging_levels_visible_in_report(login_page: Page):
    """
    Shows all logging levels.
    In the HTML report each log line appears in the test's log section.
    """
    log.debug("DEBUG: detailed internal state — only in log file")
    log.info("INFO: normal operation — appears in terminal and file")
    log.warning("WARNING: something unexpected but not fatal")
    log.error("ERROR: something went wrong — test may still pass")

    log.info(f"Current URL: {login_page.url}")
    log.info(f"Page title: {login_page.title()}")

    # This test passes — it just demonstrates logging
    assert login_page.url == BASE_URL + "/"
    log.info("Test complete: PASS")


# =============================================
# SLOW TEST — timing visible in report
# =============================================

def test_timing_visible_in_html_report(login_page: Page):
    """
    The HTML report shows duration for every test.
    You can sort by duration to find slow tests.
    Use this to identify where to optimise.
    """
    import time

    log.info("Starting timer test")
    start = time.perf_counter()

    login_page.fill("#user-name", "performance_glitch_user")
    login_page.fill("#password", "secret_sauce")
    login_page.click("#login-button")

    # performance_glitch_user has artificial delays
    login_page.wait_for_url(
        f"{BASE_URL}/inventory.html",
        timeout=15_000
    )

    duration = time.perf_counter() - start
    log.info(f"Login took {duration:.2f}s for performance_glitch_user")
    log.info("Note: this user is intentionally slow — normal")

    expect(login_page).to_have_url(f"{BASE_URL}/inventory.html")