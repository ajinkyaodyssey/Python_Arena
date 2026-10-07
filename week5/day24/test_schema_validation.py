# week5/day24/test_schema_validation.py
# Schema validation tests for reqres.in API responses
# Run with: pytest week5/day24/test_schema_validation.py -v -s

import pytest
import jsonschema
from week5.day24.schemas import (
    SINGLE_USER_RESPONSE_SCHEMA,
    LIST_USERS_RESPONSE_SCHEMA,
    CREATE_USER_RESPONSE_SCHEMA,
    UPDATE_USER_RESPONSE_SCHEMA,
    LOGIN_RESPONSE_SCHEMA,
    ERROR_RESPONSE_SCHEMA,
    USER_OBJECT_SCHEMA,
    validate_schema
)

BASE_URL = "https://reqres.in/api"


# =============================================
# SECTION 1: Single User Response Schema
# =============================================

def test_single_user_response_matches_schema(
    api_client, base_url
):
    """
    GET /api/users/2 response must match SINGLE_USER_RESPONSE_SCHEMA.

    This catches:
    - Missing required fields (id, email, first_name, etc.)
    - Wrong field types (id as string instead of integer)
    - Extra unexpected fields added by API change
    - Null values where strings are expected
    """
    resp = api_client.get(f"{base_url}/users/2")
    assert resp.status_code == 200

    validate_schema(
        resp.json(),
        SINGLE_USER_RESPONSE_SCHEMA,
        "GET /api/users/2"
    )
    print("\n  [SCHEMA] Single user response valid")
    print(f"  [SCHEMA] User: {resp.json()['data']['email']}")


def test_single_user_data_object_matches_schema(
    api_client, base_url
):
    """
    Validate just the data object in isolation.
    Useful when the same user schema appears in multiple endpoints.
    """
    resp = api_client.get(f"{base_url}/users/2")
    assert resp.status_code == 200

    user_data = resp.json()["data"]

    validate_schema(
        user_data,
        USER_OBJECT_SCHEMA,
        "data object in GET /api/users/2"
    )
    print("\n  [SCHEMA] User object valid")
    print(f"  [SCHEMA] Fields: {list(user_data.keys())}")


def test_schema_catches_missing_field():
    """
    Verify our schema correctly REJECTS a response with a missing field.

    This tests the test — confirms our schema is strict enough
    to catch real problems. If this test fails, our schema is
    too loose and not protecting us.
    """
    # Simulate a response with email missing
    bad_response = {
        "data": {
            "id": 2,
            # "email" is MISSING
            "first_name": "Janet",
            "last_name": "Weaver",
            "avatar": "https://reqres.in/img/faces/2-image.jpg"
        },
        "support": {
            "url": "https://reqres.in/#support-heading",
            "text": "To keep ReqRes free"
        }
    }

    with pytest.raises((AssertionError, jsonschema.ValidationError)):
        validate_schema(
            bad_response,
            SINGLE_USER_RESPONSE_SCHEMA,
            "missing email test"
        )

    print("\n  [SCHEMA] Correctly rejected response with missing email")


def test_schema_catches_wrong_type():
    """
    Verify schema rejects response where id is string instead of integer.
    This is a real API regression — a database change can cause this.
    """
    bad_response = {
        "data": {
            "id": "two",       # WRONG TYPE: should be integer
            "email": "janet@reqres.in",
            "first_name": "Janet",
            "last_name": "Weaver",
            "avatar": "https://reqres.in/img/faces/2-image.jpg"
        },
        "support": {
            "url": "https://reqres.in/#support-heading",
            "text": "To keep ReqRes free"
        }
    }

    with pytest.raises((AssertionError, jsonschema.ValidationError)):
        validate_schema(
            bad_response,
            SINGLE_USER_RESPONSE_SCHEMA,
            "wrong type for id"
        )

    print("\n  [SCHEMA] Correctly rejected response with id as string")


def test_schema_catches_null_required_field():
    """
    Verify schema rejects response where a required field is null.
    Null is a common API regression — field exists but has no value.
    """
    bad_response = {
        "data": {
            "id": 2,
            "email": None,     # WRONG: null where string is required
            "first_name": "Janet",
            "last_name": "Weaver",
            "avatar": "https://reqres.in/img/faces/2-image.jpg"
        },
        "support": {
            "url": "https://reqres.in/#support-heading",
            "text": "To keep ReqRes free"
        }
    }

    with pytest.raises((AssertionError, jsonschema.ValidationError)):
        validate_schema(
            bad_response,
            SINGLE_USER_RESPONSE_SCHEMA,
            "null email field"
        )

    print("\n  [SCHEMA] Correctly rejected response with null email")


# =============================================
# SECTION 2: List Users Response Schema
# =============================================

def test_list_users_response_matches_schema(
    api_client, base_url
):
    """
    GET /api/users?page=1 full response must match LIST_USERS_RESPONSE_SCHEMA.

    This validates:
    - Pagination metadata (page, per_page, total, total_pages)
    - data is an array
    - Every item in data matches USER_OBJECT_SCHEMA
    - support object is present and valid
    """
    resp = api_client.get(
        f"{base_url}/users", params={"page": 1}
    )
    assert resp.status_code == 200

    validate_schema(
        resp.json(),
        LIST_USERS_RESPONSE_SCHEMA,
        "GET /api/users?page=1"
    )

    body = resp.json()
    print("\n  [SCHEMA] List response valid")
    print(f"  [SCHEMA] Page: {body['page']}/{body['total_pages']}")
    print(f"  [SCHEMA] Users: {len(body['data'])}/{body['per_page']}")


def test_list_users_page_2_matches_schema(
    api_client, base_url
):
    """
    Page 2 must also match the schema.
    Validates that schema works across all pages, not just page 1.
    """
    resp = api_client.get(
        f"{base_url}/users", params={"page": 2}
    )
    assert resp.status_code == 200

    validate_schema(
        resp.json(),
        LIST_USERS_RESPONSE_SCHEMA,
        "GET /api/users?page=2"
    )

    body = resp.json()
    print("\n  [SCHEMA] Page 2 response valid")
    print(f"  [SCHEMA] Page 2 users: {[u['first_name'] for u in body['data']]}")


def test_every_user_in_list_matches_schema(
    api_client, base_url
):
    """
    Validate each user object individually.
    Sometimes a list has mostly valid items with one corrupted entry.
    Item-by-item validation catches that.
    """
    resp = api_client.get(f"{base_url}/users", params={"page": 1})
    assert resp.status_code == 200

    users = resp.json()["data"]
    errors = []

    for i, user in enumerate(users):
        try:
            validate_schema(
                user,
                USER_OBJECT_SCHEMA,
                f"user at index {i} (id={user.get('id')})"
            )
        except AssertionError as e:
            errors.append(f"User {i}: {str(e)[:100]}")

    assert not errors, (
        f"Schema errors in {len(errors)} users:\n" + "\n".join(errors)
    )

    print(f"\n  [SCHEMA] All {len(users)} users in list are valid")


# =============================================
# SECTION 3: Write Operation Response Schemas
# =============================================

def test_create_user_response_matches_schema(
    api_client, base_url
):
    """
    POST /api/users response must match CREATE_USER_RESPONSE_SCHEMA.
    Server-assigned fields (id, createdAt) must be present and correct type.
    """
    payload = {"name": "Schema Test User", "job": "SDET"}
    resp = api_client.post(f"{base_url}/users", json=payload)
    assert resp.status_code == 201

    validate_schema(
        resp.json(),
        CREATE_USER_RESPONSE_SCHEMA,
        "POST /api/users"
    )

    body = resp.json()
    print("\n  [SCHEMA] Create response valid")
    print(f"  [SCHEMA] id: {body['id']}, createdAt: {body['createdAt']}")


def test_update_user_put_matches_schema(
    api_client, base_url
):
    """
    PUT /api/users/2 response must match UPDATE_USER_RESPONSE_SCHEMA.
    updatedAt must be present and match timestamp pattern.
    """
    payload = {"name": "Schema Updated", "job": "Senior SDET"}
    resp = api_client.put(f"{base_url}/users/2", json=payload)
    assert resp.status_code == 200

    validate_schema(
        resp.json(),
        UPDATE_USER_RESPONSE_SCHEMA,
        "PUT /api/users/2"
    )

    print("\n  [SCHEMA] PUT response valid")
    print(f"  [SCHEMA] updatedAt: {resp.json()['updatedAt']}")


def test_update_user_patch_matches_schema(
    api_client, base_url
):
    """
    PATCH /api/users/2 response must also match UPDATE_USER_RESPONSE_SCHEMA.
    Same schema as PUT — both return name, job, updatedAt.
    """
    payload = {"name": "Schema Patched", "job": "Lead SDET"}
    resp = api_client.patch(f"{base_url}/users/2", json=payload)
    assert resp.status_code == 200

    validate_schema(
        resp.json(),
        UPDATE_USER_RESPONSE_SCHEMA,
        "PATCH /api/users/2"
    )

    print("\n  [SCHEMA] PATCH response valid")


# =============================================
# SECTION 4: Auth Response Schemas
# =============================================

def test_login_success_response_matches_schema(
    api_client, base_url
):
    """
    POST /api/login with valid credentials returns token.
    Schema validates token is present and non-empty string.
    """
    resp = api_client.post(
        f"{base_url}/login",
        json={
            "email": "eve.holt@reqres.in",
            "password": "cityslicka"
        }
    )
    assert resp.status_code == 200

    validate_schema(
        resp.json(),
        LOGIN_RESPONSE_SCHEMA,
        "POST /api/login (success)"
    )

    token = resp.json()["token"]
    print("\n  [SCHEMA] Login response valid")
    print(f"  [SCHEMA] Token: {token[:10]}...")


def test_login_failure_response_matches_schema(
    api_client, base_url
):
    """
    POST /api/login with missing password returns error.
    Error response schema validates error field is present.
    """
    resp = api_client.post(
        f"{base_url}/login",
        json={"email": "eve.holt@reqres.in"}
        # password deliberately missing
    )
    assert resp.status_code == 400

    validate_schema(
        resp.json(),
        ERROR_RESPONSE_SCHEMA,
        "POST /api/login (failure)"
    )

    error_msg = resp.json()["error"]
    print("\n  [SCHEMA] Error response valid")
    print(f"  [SCHEMA] Error: {error_msg}")


# =============================================
# SECTION 5: Schema Edge Cases
# =============================================

def test_schema_allows_valid_email_formats(api_client, base_url):
    """
    Verify our email regex pattern accepts valid emails.
    Overly strict email validation is a common mistake.
    """
    resp = api_client.get(f"{base_url}/users/2")
    assert resp.status_code == 200

    # All users should have valid emails
    user = resp.json()["data"]
    email = user["email"]

    assert "@" in email, f"Email must contain @: {email}"
    assert "." in email.split("@")[1], (
        f"Email domain must have a dot: {email}"
    )

    validate_schema(user, USER_OBJECT_SCHEMA, "email format check")
    print(f"\n  [SCHEMA] Email format valid: {email}")


def test_schema_validates_avatar_is_https_url(
    api_client, base_url
):
    """
    Avatar URLs must be HTTPS — not HTTP, not relative paths.
    Security requirement: serving user avatars over HTTP is a risk.
    """
    resp = api_client.get(f"{base_url}/users", params={"page": 1})
    assert resp.status_code == 200

    users = resp.json()["data"]

    for user in users:
        avatar = user["avatar"]
        assert avatar.startswith("https://"), (
            f"Avatar must be HTTPS URL, got: {avatar} "
            f"for user id={user['id']}"
        )

    validate_schema(
        resp.json(),
        LIST_USERS_RESPONSE_SCHEMA,
        "avatar HTTPS check"
    )
    print(f"\n  [SCHEMA] All {len(users)} avatars are HTTPS URLs")
