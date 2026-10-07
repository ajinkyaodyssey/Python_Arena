# week5/day25/conftest.py
# Auth-specific fixtures for day25.
# api_client and base_url come from week5/conftest.py automatically.

import pytest
import requests
import os
import logging
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger(__name__)

BASE_URL = "https://reqres.in/api"
VALID_EMAIL = "eve.holt@reqres.in"
VALID_PASSWORD = "cityslicka"


@pytest.fixture(scope="session")
def auth_token(api_client, base_url) -> str:
    """
    Login once per session and extract the token.
    Uses the shared api_client from week5/conftest.py
    which already has the x-api-key header set.

    Session scope: login is a network call (2-3 seconds).
    Running it once for all authenticated tests saves time.
    """
    log.info(f"Authenticating as {VALID_EMAIL}")

    resp = api_client.post(
        f"{base_url}/login",
        json={
            "email": VALID_EMAIL,
            "password": VALID_PASSWORD
        }
    )

    assert resp.status_code == 200, (
        f"Login failed during fixture setup. "
        f"Status: {resp.status_code}, "
        f"Body: {resp.text[:200]}"
    )

    body = resp.json()
    assert "token" in body, (
        f"Login response missing token. Body: {body}"
    )

    token = body["token"]
    assert len(token) > 0, "Token must not be empty"

    log.info(f"Auth successful. Token: {token[:8]}...")
    return token


@pytest.fixture(scope="session")
def auth_client(api_client, auth_token) -> requests.Session:
    """
    Authenticated session — api_client + Bearer token.
    Every request automatically carries Authorization header.

    Built on top of api_client which already has x-api-key.
    So auth_client has BOTH headers:
      x-api-key: your_key
      Authorization: Bearer token
    """
    api_client.headers.update({
        "Authorization": f"Bearer {auth_token}"
    })
    log.info(
        f"Auth client ready. "
        f"Authorization: Bearer {auth_token[:8]}..."
    )
    return api_client


# # week5/day25/conftest.py
# # Authentication fixtures for API tests.
# #
# # FIXTURE CHAIN:
# # api_client (session) — unauthenticated session, shared headers
# #     |
# #     v
# # auth_token (session) — login once, extract token, reuse
# #     |
# #     v
# # auth_client (session) — api_client + token in Authorization header
# #
# # Why all three are session-scoped:
# # - Login is a network call (2-3 seconds)
# # - Token is valid for the entire test run
# # - No test should need to re-login if the token has not expired
# # - Each test gets the same authenticated session safely because
# #   they only READ data — they do not modify the session headers

# import pytest
# import requests
# import logging

# log = logging.getLogger(__name__)

# BASE_URL = "https://reqres.in/api"

# # reqres.in test credentials — safe to use, no real data
# VALID_EMAIL = "eve.holt@reqres.in"
# VALID_PASSWORD = "cityslicka"
# INVALID_EMAIL = "invalid@reqres.in"
# INVALID_PASSWORD = "wrongpassword"


# # =============================================
# # FIXTURE 1: api_client — unauthenticated
# # =============================================

# @pytest.fixture(scope="session")
# def api_client():
#     """
#     Base unauthenticated session.
#     Used for: login endpoint itself, public endpoints,
#               testing what happens WITHOUT auth.
#     """
#     session = requests.Session()
#     session.headers.update({
#         "Content-Type": "application/json",
#         "Accept": "application/json"
#     })
#     log.info("Created unauthenticated API client")
#     yield session
#     session.close()
#     log.info("Closed API client session")


# # =============================================
# # FIXTURE 2: auth_token — extracted once
# # =============================================

# @pytest.fixture(scope="session")
# def auth_token(api_client) -> str:
#     """
#     Login once per session and extract the token.
#     Returns the raw token string.

#     Why separate from auth_client:
#     - Some tests need the token itself (to test token format,
#       to pass it manually, to test token expiry)
#     - Separating token extraction from client setup
#       follows single responsibility principle

#     Session scope: login is expensive, token is reusable.
#     """
#     log.info(f"Authenticating as {VALID_EMAIL}")

#     resp = api_client.post(
#         f"{BASE_URL}/login",
#         json={
#             "email": VALID_EMAIL,
#             "password": VALID_PASSWORD
#         }
#     )

#     assert resp.status_code == 200, (
#         f"Login failed during fixture setup. "
#         f"Status: {resp.status_code}, Body: {resp.text}"
#     )

#     body = resp.json()
#     assert "token" in body, (
#         f"Login response missing token. Body: {body}"
#     )

#     token = body["token"]
#     assert len(token) > 0, "Token must not be empty"

#     log.info(f"Authentication successful. Token: {token[:8]}...")
#     return token


# # =============================================
# # FIXTURE 3: auth_client — authenticated session
# # =============================================

# @pytest.fixture(scope="session")
# def auth_client(api_client, auth_token) -> requests.Session:
#     """
#     Authenticated session with token in Authorization header.
#     Every request made with this session automatically carries
#     the Bearer token — no manual header setting per test.

#     This is the fixture most authenticated tests should use.

#     Why modify api_client instead of creating a new session:
#     - Reuses the same TCP connection pool
#     - Keeps the same base headers (Content-Type, Accept)
#     - Adds token once — applies to all subsequent requests

#     IMPORTANT: this mutates api_client's headers.
#     If you need both authenticated and unauthenticated in one
#     test, use api_client directly and pass headers manually.
#     """
#     api_client.headers.update({
#         "Authorization": f"Bearer {auth_token}"
#     })
#     log.info(
#         f"Auth client ready. "
#         f"Authorization header: Bearer {auth_token[:8]}..."
#     )
#     return api_client


# # =============================================
# # HELPER FIXTURES
# # =============================================

# @pytest.fixture(scope="session")
# def base_url() -> str:
#     return BASE_URL


# @pytest.fixture(scope="session")
# def valid_credentials() -> dict:
#     return {
#         "email": VALID_EMAIL,
#         "password": VALID_PASSWORD
#     }


# @pytest.fixture(scope="session")
# def invalid_credentials() -> dict:
#     return {
#         "email": INVALID_EMAIL,
#         "password": INVALID_PASSWORD
#     }
