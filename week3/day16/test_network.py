# week3/day16/test_network.py
# Network interception: mock API responses inside browser tests
# Run with: pytest week3/day16/test_network.py -v -s

import json
import pytest
from playwright.sync_api import Page, Route, Request, expect

SAUCE_URL = "https://www.saucedemo.com"
INTERNET_URL = "https://the-internet.herokuapp.com"


# =============================================
# HOW page.route() WORKS
# =============================================
# page.route(url_pattern, handler_function)
# - url_pattern: glob or regex matching the request URL
# - handler_function: receives (route, request), decides what to do
#
# Inside the handler you can:
# - route.fulfill(...)  -> return a fake response
# - route.abort()       -> simulate network failure (connection refused)
# - route.continue_()   -> let the request go through normally
#
# The pattern uses glob matching:
# "**/api/users"   matches any URL ending in /api/users
# "**/*.png"       matches any URL ending in .png
# "**/inventory**" matches any URL containing /inventory


def test_intercept_and_mock_404_response(page: Page):
    """
    Intercept a specific URL pattern and return a 404.
    Use case: test how your UI handles a resource not found error.
    Without interception you cannot reliably trigger a 404
    from a real server in a test.
    """
    def handle_404(route: Route, request: Request):
        print(f"\n  [INTERCEPT] Intercepted: {request.url}")
        route.fulfill(
            status=404,
            content_type="application/json",
            body=json.dumps({"error": "Resource not found"})
        )

    # Intercept all requests to the inventory API
    page.route("**/inventory**", handle_404)

    # Navigate - the interception fires when browser requests matching URLs
    page.goto(SAUCE_URL)
    page.fill("#user-name", "standard_user")
    page.fill("#password", "secret_sauce")
    page.click("#login-button")

    print("  [INTERCEPT] 404 mock active during this test")
        
        
def test_intercept_and_mock_500_server_error(page: Page):
    """
    Mock a 500 Internal Server Error.
    Use case: verify your app shows a user-friendly error message
    instead of crashing or showing a blank page when the server fails.
    This is impossible to test reliably against a real server
    but trivial with interception.
    """
    intercepted_requests = []

    def handle_500(route: Route, request: Request):
        intercepted_requests.append(request.url)
        print(f"\n  [500] Intercepting: {request.url}")
        route.fulfill(
            status=500,
            content_type="application/json",
            body=json.dumps({
                "error": "Internal Server Error",
                "message": "Something went wrong on the server",
                "code": 500
            })
        )

    # Intercept everything going to saucedemo
    page.route(f"{SAUCE_URL}/**", handle_500)
    page.goto(SAUCE_URL)

    print(f"  [500] Intercepted {len(intercepted_requests)} requests")
    assert len(intercepted_requests) > 0, "Should have intercepted at least one request"
    
    
def test_intercept_and_return_custom_json_body(page: Page):
    """
    Return completely custom JSON data.
    Use case: test your UI with edge case data that is hard to create
    in a real database — empty arrays, null values, extremely long strings,
    special characters.
    """
    custom_response = {
        "users": [],   # empty list — test the empty state UI
        "total": 0,
        "page": 1
    }

    def handle_custom(route: Route, request: Request):
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(custom_response)
        )

    page.route("**/api/users**", handle_custom)
    page.goto(f"{INTERNET_URL}/dynamic_loading/1")

    print(f"\n  [CUSTOM] Would return empty users list if API was called")
    print(f"  [CUSTOM] Response body: {json.dumps(custom_response)}")


def test_intercept_abort_simulates_network_failure(page: Page):
    """
    route.abort() simulates a network failure — connection refused,
    DNS lookup failed, timeout. The browser never gets a response.
    Use case: test how your app handles complete network loss,
    offline mode, or failed CDN loads.
    """
    aborted_count = [0]   # list so we can mutate inside nested function

    def handle_abort(route: Route, request: Request):
        # Only abort image requests — let HTML/JS/CSS through
        if request.resource_type == "image":
            aborted_count[0] += 1
            print(f"\n  [ABORT] Aborting image request: {request.url[-50:]}")
            route.abort()
        else:
            route.continue_()   # let everything else through normally

    page.route("**/*", handle_abort)        #intercept every network request made by this page and pass it to handle_abort...   "**/*" → a URL pattern matching all requests (pages, JS, CSS, images, APIs, etc.).
    page.goto(SAUCE_URL)
    page.fill("#user-name", "standard_user")
    page.fill("#password", "secret_sauce")
    page.click("#login-button")

    print(f"\n  [ABORT] Total image requests aborted: {aborted_count[0]}")
    print("  [ABORT] Page still loaded — images just failed")
    print(f"  [ABORT] Current URL: {page.url}")
    

def test_intercept_continue_passes_through(page: Page):
    """
    route.continue_() passes the request through unchanged.
    Use case: log all requests without changing them,
    or selectively intercept only certain URLs.
    """
    all_requests = []

    def log_and_continue(route: Route, request: Request):
        all_requests.append({
            "url": request.url,
            "method": request.method,
            "type": request.resource_type
        })
        route.continue_()   # let it go through normally

    page.route("**/*", log_and_continue)
    page.goto(SAUCE_URL)

    print(f"\n  [LOG] Requests made to load {SAUCE_URL}:")
    for req in all_requests[:5]:   # show first 5
        print(f"    [{req['method']}] {req['type']}: {req['url'][-60:]}")
    print(f"  [LOG] Total requests: {len(all_requests)}")

    assert len(all_requests) > 0
    

def test_intercept_modify_response_headers(page: Page):
    """
    Modify response headers while keeping the body.
    Use case: test how your app handles specific security headers,
    CORS headers, or cache control headers.
    """
    def add_custom_header(route: Route, request: Request):
        route.fulfill(
            status=200,
            headers={
                "Content-Type": "text/html",
                "X-Custom-Test-Header": "playwright-intercepted",
                "Cache-Control": "no-cache"
            },
            body="<html><body><h1>Intercepted Response</h1></body></html>"
        )

    page.route("**/some-api-endpoint**", add_custom_header)

    # Route is set but won't fire unless that URL is requested
    # Demonstrate the concept by going to a real page
    page.goto(SAUCE_URL)
    print("\n  [HEADERS] Custom header route registered")
    print("  [HEADERS] Would fire on **/some-api-endpoint** requests")
    
    
def test_intercept_only_post_requests(page: Page):
    """
    Selectively intercept only POST requests.
    Use case: mock form submissions or API mutations
    without affecting GET requests (page loads).
    """
    intercepted_posts = []

    def handle_posts_only(route: Route, request: Request):
        if request.method == "POST":
            intercepted_posts.append(request.url)
            print(f"\n  [POST] Intercepted POST to: {request.url}")
            route.fulfill(
                status=201,
                content_type="application/json",
                body=json.dumps({"id": 999, "created": True})
            )
        else:
            route.continue_()

    page.route("**/*", handle_posts_only)
    page.goto(f"{INTERNET_URL}/login")

    # Submit the login form — this sends a POST
    page.fill("#username", "tomsmith")
    page.fill("#password", "SuperSecretPassword!")
    page.locator("button[type='submit']").click()

    print(f"  [POST] Total POST requests intercepted: {len(intercepted_posts)}")