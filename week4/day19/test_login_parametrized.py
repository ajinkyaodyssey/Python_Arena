# week4/day19/test_login_parametrized.py
# Parametrized login tests with smoke and regression markers
# Run with:
#   pytest week4/day19/test_login_parametrized.py -v
#   pytest week4/day19/test_login_parametrized.py -m smoke -v
#   pytest week4/day19/test_login_parametrized.py -m regression -v

import pytest
from playwright.sync_api import sync_playwright, Page, expect

BASE_URL = "https://www.saucedemo.com"
USERNAME = "#user-name"
PASSWORD = "#password"
LOGIN_BTN = "#login-button"
ERROR_MSG = "[data-test='error']"


# =============================================
# FIXTURES (inline for this file)
# =============================================

@pytest.fixture(scope = "session")
def browser():
    with sync_playwright() as p:
        br = p.chromium.launch(headless = True)
        yield br
        br.close()
        

@pytest.fixture(scope = "function")
def login_page(browser):
    ctx = browser.new_context(viewport = {"width": 1280, "height": 720})
    ctx.set_default_timeout(15_000)
    pg = ctx.new_page()
    pg.goto(BASE_URL)
    yield pg
    ctx.close()
    

# =============================================
# SMOKE TESTS
# =============================================
# Critical path only. Run on every commit.
# If smoke fails: block the merge immediately.
# Target: complete in under 2 minutes.

@pytest.mark.smoke
def test_valid_login_smoke(login_page: Page):
    """
    The most critical test in the suite.
    If login does not work, nothing else matters.
    Marked smoke so it runs on every single commit.
    """
    login_page.fill(USERNAME, "standard_user")
    login_page.fill(PASSWORD, "secret_sauce")
    login_page.click(LOGIN_BTN)

    expect(login_page).to_have_url(f"{BASE_URL}/inventory.html")
    expect(login_page.locator(".title")).to_have_text("Products")
    expect(login_page.locator(".inventory_item")).to_have_count(6)
    

@pytest.mark.smoke
def test_invalid_login_shows_error_smoke(login_page: Page):
    """
    Verify the error message system works.
    Second most critical login test.
    """
    login_page.fill(USERNAME, "wrong_user")
    login_page.fill(PASSWORD, "wrong_pass")
    login_page.click(LOGIN_BTN)

    expect(login_page.locator(ERROR_MSG)).to_be_visible()
    expect(login_page).to_have_url(f"{BASE_URL}/")
    

# =============================================
# PARAMETRIZED INVALID LOGIN — 1 test, 5 scenarios
# =============================================
# BEFORE: 5 separate test functions, 5 places to update
# AFTER:  1 function, 5 data rows, 1 place to update
#
# Each row is: (username, password, expected_error_text, test_id)


INVALID_LOGIN_SCENARIOS = [
    pytest.param(
        "wrong_user",
        "secret_sauce",
        "Username and password do not match",
        id="wrong_username"
    ),
    pytest.param(
        "standard_user",
        "wrong_password",
        "Username and password do not match",
        id="wrong_password"
    ),
    pytest.param(
        "",
        "secret_sauce",
        "Username is required",
        id="empty_username"
    ),
    pytest.param(
        "standard_user",
        "",
        "Password is required",
        id="empty_password"
    ),
    pytest.param(
        "locked_out_user",
        "secret_sauce",
        "Sorry, this user has been locked out",
        id="locked_user"
    ),
]


@pytest.mark.regression
@pytest.mark.parametrize("username, password, expected_error",
                         INVALID_LOGIN_SCENARIOS)
def test_invalid_login_scenarios(
    login_page: Page,
    username: str,
    password: str,
    expected_error: str
):
    """
    5 invalid login scenarios in 1 parametrized test.

    pytest generates 5 separate test runs:
    - test_invalid_login_scenarios[wrong_username]
    - test_invalid_login_scenarios[wrong_password]
    - test_invalid_login_scenarios[empty_username]
    - test_invalid_login_scenarios[empty_password]
    - test_invalid_login_scenarios[locked_user]

    Each gets its own pass/fail status in the report.
    One failing scenario does not block the others.
    """
    login_page.fill(USERNAME, username)
    login_page.fill(PASSWORD, password)
    login_page.click(LOGIN_BTN)

    expect(login_page.locator(ERROR_MSG)).to_be_visible()
    expect(login_page.locator(ERROR_MSG)).to_contain_text(expected_error)
    expect(login_page).to_have_url(f"{BASE_URL}/")
    

# =============================================
# PARAMETRIZED VALID USERS
# =============================================
# saucedemo has multiple valid user types.
# Each has slightly different behaviour.

# =============================================
# PARAMETRIZED VALID USERS
# =============================================
# saucedemo has multiple valid user types.
# Each has slightly different behaviour.

VALID_USER_SCENARIOS = [
    pytest.param(
        "standard_user",
        "secret_sauce",
        "/inventory.html",
        id="standard_user"
    ),
    pytest.param(
        "performance_glitch_user",
        "secret_sauce",
        "/inventory.html",
        id="performance_glitch_user"
    ),
]


@pytest.mark.regression
@pytest.mark.slow
@pytest.mark.parametrize(
    "username, password, expected_path",
    VALID_USER_SCENARIOS
)
def test_valid_users_reach_inventory(
    login_page: Page,
    username: str,
    password: str,
    expected_path: str
):
    """
    All valid user types should reach the inventory page.
    Marked slow because performance_glitch_user has artificial delays.
    """
    login_page.fill(USERNAME, username)
    login_page.fill(PASSWORD, password)
    login_page.click(LOGIN_BTN)

    expect(login_page).to_have_url(f"{BASE_URL}{expected_path}")


# =============================================
# COMBINED SMOKE + PARAMETRIZE
# =============================================
# You can stack marks. A test can be both smoke AND parametrized.
# Use when you want a small subset of parametrized cases in smoke.

CRITICAL_ERROR_SCENARIOS = [
    pytest.param(
        "", "", "Username is required",
        id="both_empty"
    ),
    pytest.param(
        "standard_user", "wrong", "Username and password do not match",
        id="wrong_pass_valid_user"
    ),
]


@pytest.mark.smoke
@pytest.mark.parametrize(
    "username, password, expected_error",
    CRITICAL_ERROR_SCENARIOS
)
def test_critical_error_scenarios_smoke(
    login_page: Page,
    username: str,
    password: str,
    expected_error: str
):
    """
    The 2 most important error cases, in smoke suite.
    Empty fields and wrong password for valid user.
    """
    login_page.fill(USERNAME, username)
    login_page.fill(PASSWORD, password)
    login_page.click(LOGIN_BTN)

    expect(login_page.locator(ERROR_MSG)).to_contain_text(expected_error)


# =============================================
# xfail — expected failure
# =============================================

@pytest.mark.regression
@pytest.mark.xfail(
    reason="saucedemo does not implement rate limiting — known gap",
    strict=False
)
def test_multiple_failed_logins_triggers_lockout(login_page: Page):
    """
    A real app should lock an account after N failed attempts.
    saucedemo does not implement this — test is expected to fail.
    xfail means: we know this fails, do not count it as a suite failure.
    strict=False means: if it accidentally passes, mark as xpass (not error).
    """
    for i in range(5):
        login_page.fill(USERNAME, "standard_user")
        login_page.fill(PASSWORD, f"wrong_attempt_{i}")
        login_page.click(LOGIN_BTN)
        login_page.goto(BASE_URL)

    login_page.fill(USERNAME, "standard_user")
    login_page.fill(PASSWORD, "secret_sauce")
    login_page.click(LOGIN_BTN)

    # This assertion will fail — account not locked
    expect(login_page.locator(ERROR_MSG)).to_contain_text("locked")


# =============================================
# skipif — conditional skip
# =============================================

import os

@pytest.mark.regression
@pytest.mark.skipif(
    os.getenv("CI") is None,
    reason="This test only runs in CI environment"
)
def test_login_in_ci_only(login_page: Page):
    """
    Some tests should only run in CI.
    skipif: if CI env var is not set, skip this test.
    In GitHub Actions, CI=true is set automatically.
    Locally, it is not set, so the test is skipped.
    """
    login_page.fill(USERNAME, "standard_user")
    login_page.fill(PASSWORD, "secret_sauce")
    login_page.click(LOGIN_BTN)
    expect(login_page).to_have_url(f"{BASE_URL}/inventory.html")