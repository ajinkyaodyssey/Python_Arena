

# week5/day22/conftest.py
# day22-specific fixtures only.
# api_client and base_url come from week5/conftest.py automatically.
# pytest loads parent conftest files before child ones.

# No fixtures needed here for day22 — all provided by week5/conftest.py



# ------------------------------------------------------

# # week5/day22/conftest.py
# # Fixtures for API tests.
# # No browser, no Playwright — pure HTTP.

# import pytest
# import requests

# BASE_URL = "https://reqres.in/api"  # Base address for API


# @pytest.fixture(scope="session")
# def api_client():
#     """
#     Session-scoped requests.Session.

#     Why Session() instead of bare requests.get():
#     - Session reuses the TCP connection across requests (connection pooling)
#       This makes a suite of sequential API calls significantly faster
#     - Session stores headers set once — no need to repeat on every call
#     - Session stores cookies — essential for authenticated flows
#     - Mirrors how a real user session behaves

#     Session scope: created once for all tests, closed after all tests.
#     Session = reusable HTTP client that remembers things between requests, i.e  it does maintain state — notably cookies, headers, and connection pooling.
#     """
#     session = requests.Session()  # Create reusable HTTP client
#     session.headers.update({
#         "Content-Type": "application/json",  # Data being sent is JSON
#         "Accept": "application/json"         # Want JSON response
#     })
#     yield session  # Give session to the test; fixture pauses here
#     session.close()  # Close session after all tests


# @pytest.fixture(scope="session")
# def base_url() -> str:
#     """Base URL for all API calls. Single point of change."""
#     return BASE_URL  # Return URL to the test