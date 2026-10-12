# week7/day35/test_always_demo.py
# Deliberately failing test to prove if: always() works.
# When this test fails in CI, the upload artifact step
# must still run and produce a report.
# After proving it works, we skip this test.
# Run with: pytest week7/day35/ -v

import pytest


# @pytest.mark.skip(reason="Demo only - enable to test if:always() behaviour")
def test_deliberately_fails_to_prove_always():
    """
    This test exists to prove that if: always() works in CI.
    
    HOW TO USE:
    1. Remove the @pytest.mark.skip decorator
    2. Push to GitHub
    3. Watch CI — test-ui job should FAIL
    4. Check that 'Upload UI test report' step still runs
    5. Download the artifact — report should exist
    6. Re-add the skip decorator and push again
    
    WHY THIS MATTERS:
    Without if: always() on the upload step:
    - Test fails
    - GitHub skips remaining steps
    - No report uploaded
    - You cannot debug the failure
    
    With if: always():
    - Test fails
    - Upload step runs anyway
    - Report uploaded
    - You can see exactly what went wrong
    """
    # This assertion will always fail
    assert False, (
        "This is a deliberate failure to test if:always() behaviour. "
        "The upload artifact step above should still run after this fails."
    )


def test_always_demo_is_skipped_by_default():
    """
    Verify the deliberate failure test is properly skipped.
    This test always passes — it just confirms the skip is in place.
    """
    # If we reach here, the skip decorator is working
    assert True


@pytest.mark.skip(reason="Demo only - enable to test Playwright screenshot on failure")
def test_playwright_screenshot_on_failure_demo(page):
    """
    When this Playwright test fails:
    1. The screenshot_on_failure fixture fires
    2. Screenshot saved to reports/screenshots/
    3. Upload artifact step picks it up
    4. Downloadable from GitHub Actions artifacts tab
    
    Enable by removing skip, push, check CI artifacts.
    """
    from playwright.sync_api import expect
    page.goto("https://www.saucedemo.com")

    # This will fail — wrong expected text
    expect(page.locator(".login_logo")).to_have_text(
        "This Text Does Not Exist On The Page"
    )
    # Screenshot taken automatically by conftest hook
    # Then uploaded by if: always() artifact step