# week5/day25/test_auth_flow.py
# Complete authentication flow tests:
# - Login endpoint (success + failure)
# - Token extraction and validation
# - Token usage in subsequent requests
# - Session fixture reuse demonstration
# Run with: pytest week5/day25/test_auth_flow.py -v -s

import requests
from week5.day24.schemas import (
    LOGIN_RESPONSE_SCHEMA,
    ERROR_RESPONSE_SCHEMA,
    validate_schema
)

BASE_URL = "https://reqres.in/api"


# =============================================
# SECTION 1: Login Endpoint
# =============================================

def test_login_with_valid_credentials_returns_200(
    api_client, base_url, valid_credentials
):
    """
    POST /api/login with valid credentials.

    What we verify:
    - Status 200 (not 201 — login is not creating a resource)
    - Response contains token field
    - Token is a non-empty string
    - Schema is correct
    """
    resp = api_client.post(
        f"{base_url}/login",
        json=valid_credentials
    )

    assert resp.status_code == 200, (
        f"Login should return 200, got {resp.status_code}. "
        f"Body: {resp.text}"
    )

    body = resp.json()
    validate_schema(body, LOGIN_RESPONSE_SCHEMA, "POST /api/login")

    assert "token" in body
    assert isinstance(body["token"], str)
    assert len(body["token"]) > 0

    print(f"\n  [LOGIN] Status: {resp.status_code}")
    print(f"  [LOGIN] Token received: {body['token'][:8]}...")
    print(f"  [LOGIN] Token length: {len(body['token'])} chars")


def test_login_with_missing_password_returns_400(
    api_client, base_url
):
    """
    POST /api/login without password.

    Real APIs validate required fields. Missing password
    should return 400 Bad Request with an error message.
    This is NOT a 401 — 401 means auth failed, 400 means
    the request itself is malformed.
    """
    resp = api_client.post(
        f"{base_url}/login",
        json={"email": "eve.holt@reqres.in"}
        # password field deliberately missing
    )

    assert resp.status_code == 400, (
        f"Missing password should return 400, got {resp.status_code}"
    )

    body = resp.json()
    validate_schema(body, ERROR_RESPONSE_SCHEMA, "login missing password")

    assert "error" in body
    error_msg = body["error"]
    assert len(error_msg) > 0

    print(f"\n  [LOGIN FAIL] Status: {resp.status_code}")
    print(f"  [LOGIN FAIL] Error: {error_msg}")


def test_login_with_missing_email_returns_400(
    api_client, base_url
):
    """
    POST /api/login without email.
    Email is also a required field — missing it should be 400.
    """
    resp = api_client.post(
        f"{base_url}/login",
        json={"password": "cityslicka"}
        # email field deliberately missing
    )

    assert resp.status_code == 400, (
        f"Missing email should return 400, got {resp.status_code}"
    )

    body = resp.json()
    assert "error" in body

    print(f"\n  [LOGIN FAIL] Missing email: {resp.status_code}")
    print(f"  [LOGIN FAIL] Error: {body['error']}")


def test_login_with_wrong_credentials_returns_400(
    api_client, base_url, invalid_credentials
):
    """
    POST /api/login with wrong credentials.

    reqres.in returns 400 for unrecognised credentials.
    Real production APIs vary:
    - Some return 401 (Unauthorized — credentials wrong)
    - Some return 400 (Bad Request — deliberately vague for security)
    Being vague (400) is actually more secure — it does not confirm
    whether the email exists or the password is wrong.
    """
    resp = api_client.post(
        f"{base_url}/login",
        json=invalid_credentials
    )

    # reqres.in returns 400 for unrecognised user
    assert resp.status_code in [400, 401], (
        f"Wrong credentials should return 400 or 401, "
        f"got {resp.status_code}"
    )

    body = resp.json()
    assert "error" in body

    print(f"\n  [LOGIN FAIL] Wrong creds: {resp.status_code}")
    print(f"  [LOGIN FAIL] Error: {body['error']}")


def test_login_with_empty_body_returns_400(
    api_client, base_url
):
    """
    POST /api/login with completely empty body.
    Server must validate that required fields exist.
    """
    resp = api_client.post(
        f"{base_url}/login",
        json={}
    )

    assert resp.status_code == 400, (
        f"Empty body should return 400, got {resp.status_code}"
    )

    print(f"\n  [LOGIN FAIL] Empty body: {resp.status_code}")
    print(f"  [LOGIN FAIL] Body: {resp.json()}")


# =============================================
# SECTION 2: Token Extraction and Validation
# =============================================

def test_auth_token_fixture_provides_valid_token(auth_token):
    """
    Verify the auth_token fixture gives a usable token.
    This tests our test infrastructure — if the token fixture
    is broken, all authenticated tests will fail for the wrong reason.
    """
    # Token must be a non-empty string
    assert isinstance(auth_token, str), (
        f"Token should be string, got {type(auth_token).__name__}"
    )
    assert len(auth_token) > 0, "Token must not be empty"

    # reqres.in tokens are typically short alphanumeric strings
    assert auth_token.isalnum() or len(auth_token) > 5, (
        f"Token looks invalid: {auth_token}"
    )

    print(f"\n  [TOKEN] Token type: {type(auth_token).__name__}")
    print(f"  [TOKEN] Token length: {len(auth_token)}")
    print(f"  [TOKEN] Token preview: {auth_token[:8]}...")


def test_token_format_is_consistent(api_client, base_url):
    """
    Two login calls should return the same token for the same user.
    reqres.in returns a fixed token per user — consistency check.

    On a real JWT-based API, two logins return DIFFERENT tokens
    (each with a different expiry time). This test would need to
    verify the token structure (header.payload.signature) instead.
    """
    credentials = {
        "email": "eve.holt@reqres.in",
        "password": "cityslicka"
    }

    resp1 = api_client.post(f"{base_url}/login", json=credentials)
    resp2 = api_client.post(f"{base_url}/login", json=credentials)

    assert resp1.status_code == 200
    assert resp2.status_code == 200

    token1 = resp1.json()["token"]
    token2 = resp2.json()["token"]

    # reqres.in returns same token — deterministic
    assert token1 == token2, (
        f"reqres.in should return consistent token for same user. "
        f"Got different tokens: {token1} vs {token2}"
    )

    print(f"\n  [TOKEN] Token 1: {token1[:8]}...")
    print(f"  [TOKEN] Token 2: {token2[:8]}...")
    print(f"  [TOKEN] Consistent: {token1 == token2}")


# =============================================
# SECTION 3: Using Token in Requests
# =============================================

def test_auth_client_fixture_has_authorization_header(
    auth_client
):
    """
    Verify the auth_client fixture has Authorization header set.
    Tests the fixture itself before testing any real endpoint.
    """
    assert "Authorization" in auth_client.headers, (
        "auth_client must have Authorization header"
    )

    auth_header = auth_client.headers["Authorization"]
    assert auth_header.startswith("Bearer "), (
        f"Authorization must start with 'Bearer ', got: {auth_header}"
    )

    token_part = auth_header.replace("Bearer ", "")
    assert len(token_part) > 0, "Token part of Authorization header is empty"

    print(f"\n  [AUTH CLIENT] Authorization: {auth_header[:20]}...")


def test_authenticated_request_to_user_endpoint(
    auth_client, base_url
):
    """
    Make a request with the auth token in the header.
    GET /api/users/2 with Authorization header.

    reqres.in does not actually require auth for GET endpoints —
    this demonstrates the PATTERN of making authenticated requests.
    On a real protected API, this same pattern would be required.
    """
    resp = auth_client.get(f"{base_url}/users/2")

    assert resp.status_code == 200, (
        f"Authenticated GET should return 200, got {resp.status_code}"
    )

    body = resp.json()
    assert "data" in body
    assert body["data"]["id"] == 2

    # Confirm Authorization header was sent
    print(f"\n  [AUTH REQUEST] Status: {resp.status_code}")
    print(f"  [AUTH REQUEST] Authorization header was: "
          f"{auth_client.headers.get('Authorization', 'NOT SET')[:20]}...")
    print(f"  [AUTH REQUEST] User retrieved: "
          f"{body['data']['first_name']} {body['data']['last_name']}")


def test_manually_set_token_in_header(
    api_client, auth_token, base_url
):
    """
    Demonstrate manually passing token per-request.
    Alternative to auth_client fixture when you need fine-grained control.

    Use case: testing what happens when you send:
    - A different token format
    - An expired token (mock)
    - A token from a different user
    """
    # Pass token manually in this specific request only
    resp = api_client.get(
        f"{base_url}/users/2",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert resp.status_code == 200

    print(f"\n  [MANUAL TOKEN] Manually set token, got: {resp.status_code}")


def test_request_without_token_still_works_on_public_endpoint(
    api_client, base_url
):
    """
    reqres.in public endpoints work without authentication.
    This test confirms which endpoints are truly public.

    On a real API with protected endpoints, removing the token
    from a request to a protected endpoint should return 401.
    This pattern is how you test that your auth is actually
    protecting what it should protect.
    """
    # Make request with no Authorization header
    resp = requests.get(
        f"{base_url}/users/2",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
            # Deliberately NO Authorization header
        }
    )

    # reqres.in is public — works without token
    assert resp.status_code == 200

    print(f"\n  [NO TOKEN] Public endpoint without token: {resp.status_code}")
    print("  [NO TOKEN] NOTE: reqres.in has no truly protected endpoints.")
    print("  [NOTE] On a real API, removing token on protected")
    print("         endpoint should return 401.")


# =============================================
# SECTION 4: Complete Auth Flow End-to-End
# =============================================

def test_complete_auth_flow_login_then_use_token(
    api_client, base_url
):
    """
    Complete authentication flow in a single test.
    This is the pattern you use in a real test suite:

    Step 1: Login → get token
    Step 2: Set token in session headers
    Step 3: Make authenticated request
    Step 4: Verify response

    This test does not use the auth_client fixture —
    it builds the auth flow from scratch to demonstrate
    the complete sequence clearly.
    """
    print("\n  [FULL FLOW] Starting complete auth flow")

    print("\n  [FULL FLOW] Starting complete auth flow")

    # STEP 1: Login using existing api_client (has x-api-key)
    print("  [FULL FLOW] Step 1: Login")
    login_resp = api_client.post(
        f"{base_url}/login",
        json={
            "email": "eve.holt@reqres.in",
            "password": "cityslicka"
        }
    )

    assert login_resp.status_code == 200
    token = login_resp.json()["token"]
    print(f"  [FULL FLOW] Token obtained: {token[:8]}...")

    # STEP 2: Add Bearer token to existing session
    print("  [FULL FLOW] Step 2: Set Authorization header")
    api_client.headers["Authorization"] = f"Bearer {token}"

    # STEP 3: Make authenticated request
    print("  [FULL FLOW] Step 3: Make authenticated request")
    user_resp = api_client.get(f"{base_url}/users/2")

    assert user_resp.status_code == 200, (
        f"Authenticated request failed: {user_resp.status_code}"
    )

    # STEP 4: Verify
    print("  [FULL FLOW] Step 4: Verify response")
    user = user_resp.json()["data"]
    assert user["id"] == 2

    print(f"  [FULL FLOW] Success! User: {user['first_name']} {user['last_name']}")

    # Clean up — remove Bearer token so it doesn't affect other tests
    api_client.headers.pop("Authorization", None)


def test_auth_session_fixture_faster_than_login_per_test(
    auth_client, base_url
):
    """
    Demonstrate that auth_client fixture is already authenticated.
    Makes multiple calls without any login overhead.

    This is the speed argument for the session-scoped auth fixture:
    - 10 authenticated tests
    - Without fixture: 10 logins = 10 * 2s = 20 seconds overhead
    - With fixture: 1 login = 2 seconds overhead total
    """
    import time

    # Make 3 calls — no login needed, all use cached token
    start = time.perf_counter()

    resp1 = auth_client.get(f"{base_url}/users/1")
    resp2 = auth_client.get(f"{base_url}/users/2")
    resp3 = auth_client.get(f"{base_url}/users/3")

    total = time.perf_counter() - start

    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp3.status_code == 200

    print(f"\n  [SPEED] 3 authenticated requests in {total:.3f}s")
    print("  [SPEED] No login overhead — token reused from fixture")
    print("  [SPEED] If login per test: add ~6s of overhead for 3 tests")


# =============================================
# SECTION 5: Register Endpoint
# =============================================

def test_register_new_user_returns_token(api_client, base_url):
    """
    POST /api/register — register a new user.
    Returns both id and token.

    reqres.in only supports specific test emails.
    Use the documented test email for registration.
    """
    resp = api_client.post(
        f"{base_url}/register",
        json={
            "email": "eve.holt@reqres.in",
            "password": "pistol"
        }
    )

    assert resp.status_code == 200, (
        f"Registration should return 200, got {resp.status_code}. "
        f"Body: {resp.text}"
    )

    body = resp.json()
    assert "id" in body, "Register response must contain id"
    assert "token" in body, "Register response must contain token"
    assert len(body["token"]) > 0

    print(f"\n  [REGISTER] Status: {resp.status_code}")
    print(f"  [REGISTER] ID: {body['id']}")
    print(f"  [REGISTER] Token: {body['token'][:8]}...")


def test_register_without_password_returns_400(
    api_client, base_url
):
    """
    POST /api/register without password.
    Registration should validate required fields.
    """
    resp = api_client.post(
        f"{base_url}/register",
        json={"email": "sydney@fife"}
        # password missing
    )

    assert resp.status_code == 400

    body = resp.json()
    assert "error" in body
    print(f"\n  [REGISTER FAIL] Missing password: {body['error']}")
