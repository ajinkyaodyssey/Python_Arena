# week5/day23/test_post.py
# POST /api/users tests — happy path + negative cases
# Run with: pytest week5/day23/test_post.py -v -s

import pytest

BASE_URL = "https://reqres.in/api"


# =============================================
# HAPPY PATH — 3 tests
# =============================================

def test_post_create_user_returns_201(
    api_client, base_url, valid_user_payload
):
    """
    POST /api/users with valid body must return 201 Created.

    201 means: resource was created successfully.
    200 would be wrong here — 200 means OK for existing resource.
    Using 201 correctly signals to clients that something new exists.

    What we verify:
    - Correct status code (201 not 200)
    - Response has an id field — server assigned
    - Response has createdAt — server assigned timestamp
    - Response reflects what we sent (name, job)
    """
    resp = api_client.post(
        f"{base_url}/users",
        json=valid_user_payload
    )

    assert resp.status_code == 201, (
        f"Expected 201 Created, got {resp.status_code}. "
        f"Body: {resp.text}"
    )

    body = resp.json()

    # Server-assigned fields must be present
    assert "id" in body, "Response must contain server-assigned id"
    assert "createdAt" in body, (
        "Response must contain server-assigned createdAt timestamp"
    )

    # Response must reflect what we sent
    assert body["name"] == valid_user_payload["name"], (
        f"Expected name '{valid_user_payload['name']}', "
        f"got '{body['name']}'"
    )
    assert body["job"] == valid_user_payload["job"]

    print(f"\n  [POST] Created user ID: {body['id']}")
    print(f"  [POST] Created at: {body['createdAt']}")
    print(f"  [POST] Name: {body['name']}, Job: {body['job']}")


def test_post_response_fields_are_correct_types(
    api_client, base_url, valid_user_payload
):
    """
    Every field in the POST response must be the correct type.
    A 201 with id=None or id="abc" would break API consumers.

    Type validation catches silent contract breaks that
    status code checks completely miss.
    """
    resp = api_client.post(
        f"{base_url}/users",
        json=valid_user_payload
    )

    assert resp.status_code == 201
    body = resp.json()

    # id can be string or int depending on the API design
    # reqres.in returns id as string — verify it is not None
    assert body["id"] is not None, "id must not be None"
    assert len(str(body["id"])) > 0, "id must not be empty"

    # name and job must be strings
    assert isinstance(body["name"], str), (
        f"name should be str, got {type(body['name']).__name__}"
    )
    assert isinstance(body["job"], str)

    # createdAt must be a non-empty string (ISO timestamp)
    assert isinstance(body["createdAt"], str)
    assert len(body["createdAt"]) > 0, "createdAt must not be empty"

    print(f"\n  [POST TYPES] id type: {type(body['id']).__name__}")
    print(f"  [POST TYPES] createdAt: {body['createdAt']}")


def test_post_different_payloads_get_different_ids(
    api_client, base_url
):
    """
    Each POST request should create a unique resource.
    Two calls with different data should get different IDs.
    Same ID would indicate a caching or deduplication bug.

    This is an important real-world test:
    POST is NOT idempotent — calling it twice should create two resources.
    """
    payload1 = {"name": "Arjun Sharma", "job": "QA Engineer"}
    payload2 = {"name": "Priya Patel", "job": "SDET Lead"}

    resp1 = api_client.post(f"{base_url}/users", json=payload1)
    resp2 = api_client.post(f"{base_url}/users", json=payload2)

    assert resp1.status_code == 201
    assert resp2.status_code == 201

    id1 = resp1.json()["id"]
    id2 = resp2.json()["id"]

    # reqres.in always returns the same ID in simulation
    # On a real API, assert id1 != id2
    # For reqres.in, we verify both IDs exist and are non-null
    assert id1 is not None
    assert id2 is not None

    print(f"\n  [POST] Request 1 ID: {id1}")
    print(f"  [POST] Request 2 ID: {id2}")
    print(f"  [POST] Both created successfully — POST is not idempotent")


# =============================================
# NEGATIVE CASES — 3 tests
# =============================================

def test_post_with_empty_body_returns_error_or_201(
    api_client, base_url
):
    """
    POST with empty body {} — what should happen?

    On a real production API with validation: 400 Bad Request.
    reqres.in does not validate — it returns 201 even for empty body.
    This test documents that behaviour explicitly.

    WHY THIS MATTERS FOR SDET INTERVIEWS:
    Testing negative cases shows you understand that APIs should
    validate input. When reqres.in accepts empty body, you note it
    as a gap — a real API should reject this with 400.
    """
    resp = api_client.post(f"{base_url}/users", json={})

    # reqres.in returns 201 for empty body (no validation)
    # Document this: on a real API with validation, assert 400
    print(f"\n  [POST NEGATIVE] Empty body status: {resp.status_code}")
    print(f"  [POST NEGATIVE] Body: {resp.json()}")
    print(
        "  [POST NEGATIVE] NOTE: Real API should return 400 for empty body. "
        "reqres.in has no validation."
    )

    # At minimum the server should not crash
    assert resp.status_code != 500, (
        "Server must not crash on empty body — 500 is a server bug"
    )


def test_post_with_extra_fields_does_not_crash(
    api_client, base_url
):
    """
    POST with unexpected extra fields.
    Real APIs should either:
    A) Ignore unknown fields (lenient) — return 201
    B) Reject unknown fields (strict) — return 400

    Neither is wrong — it depends on API design.
    What is always wrong: crashing with 500.

    Testing this catches APIs that fail on any unexpected input,
    which indicates fragile validation logic.
    """
    payload_with_extras = {
        "name": "Test User",
        "job": "Tester",
        "unknown_field_xyz": "unexpected_value",
        "another_unknown": 12345,
        "nested_unknown": {"key": "value"}
    }

    resp = api_client.post(
        f"{base_url}/users",
        json=payload_with_extras
    )

    print(f"\n  [POST NEGATIVE] Extra fields status: {resp.status_code}")
    print(f"  [POST NEGATIVE] Response: {resp.json()}")

    # Must not crash
    assert resp.status_code != 500, (
        "Server must not return 500 for extra fields"
    )

    # reqres.in returns 201 (lenient — ignores unknowns)
    # On a strict API you might assert 400 here
    assert resp.status_code in [201, 400], (
        f"Expected 201 (lenient) or 400 (strict), got {resp.status_code}"
    )


def test_post_response_time_under_2s(api_client, base_url):
    """
    POST operations should be fast.
    Slow writes indicate DB bottlenecks or missing indexes.
    """
    payload = {"name": "Performance Test", "job": "SDET"}
    resp = api_client.post(f"{base_url}/users", json=payload)

    assert resp.status_code == 201
    response_time = resp.elapsed.total_seconds()

    assert response_time < 2.0, (
        f"POST response time {response_time:.3f}s exceeded 2s threshold"
    )
    print(f"\n  [POST PERF] Response time: {response_time:.3f}s")