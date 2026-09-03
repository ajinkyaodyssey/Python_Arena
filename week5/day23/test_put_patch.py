# week5/day23/test_put_patch.py
# PUT /api/users/{id} and PATCH /api/users/{id} tests
# Run with: pytest week5/day23/test_put_patch.py -v -s

import pytest

BASE_URL = "https://reqres.in/api"
VALID_USER_ID = 2     # Janet Weaver — known to exist


# =============================================
# PUT TESTS — Full replacement
# =============================================

def test_put_user_returns_200(api_client, base_url):
    """
    PUT /api/users/2 with complete body returns 200.

    PUT = full replacement of the resource.
    You send the ENTIRE resource — all fields.
    Fields you omit are removed/reset to defaults.
    This is different from PATCH which is partial.

    What we verify:
    - Status 200 (not 201 — resource already exists)
    - Response reflects exactly what we sent
    - updatedAt timestamp appears (server-assigned)
    """
    payload = {
        "name": "Janet Updated",
        "job": "Senior Engineer"
    }

    resp = api_client.put(
        f"{base_url}/users/{VALID_USER_ID}",
        json=payload
    )

    assert resp.status_code == 200, (
        f"Expected 200, got {resp.status_code}. Body: {resp.text}"
    )

    body = resp.json()

    assert body["name"] == payload["name"], (
        f"Expected name '{payload['name']}', got '{body['name']}'"
    )
    assert body["job"] == payload["job"]
    assert "updatedAt" in body, (
        "PUT response must contain server-assigned updatedAt"
    )
    assert len(body["updatedAt"]) > 0

    print(f"\n  [PUT] Updated user {VALID_USER_ID}")
    print(f"  [PUT] Name: {body['name']}, Job: {body['job']}")
    print(f"  [PUT] Updated at: {body['updatedAt']}")


def test_put_response_reflects_new_data(api_client, base_url):
    """
    PUT response must contain exactly what we sent.
    If the response echoes old data, the update did not work.

    Send unique values so we can be sure the response
    is not just returning cached old data.
    """
    import uuid
    unique_name = f"Test User {uuid.uuid4().hex[:8]}"
    unique_job = f"Role {uuid.uuid4().hex[:8]}"

    payload = {"name": unique_name, "job": unique_job}
    resp = api_client.put(
        f"{base_url}/users/{VALID_USER_ID}",
        json=payload
    )

    assert resp.status_code == 200
    body = resp.json()

    assert body["name"] == unique_name, (
        f"Response name '{body['name']}' does not match "
        f"sent name '{unique_name}'"
    )
    assert body["job"] == unique_job, (
        f"Response job '{body['job']}' does not match "
        f"sent job '{unique_job}'"
    )

    print(f"\n  [PUT] Unique name verified: {unique_name[:20]}...")


def test_put_nonexistent_user(api_client, base_url):
    """
    PUT to a nonexistent user ID.

    Different APIs handle this differently:
    - Some return 404 (resource not found — cannot replace)
    - Some return 200/201 (upsert — create if not exists)
    - reqres.in returns 200 (simulation — no real lookup)

    This test documents the API's behaviour.
    On a real API you would decide which behaviour
    is correct for your system and assert accordingly.
    """
    payload = {"name": "Ghost User", "job": "Phantom"}

    resp = api_client.put(
        f"{base_url}/users/9999",
        json=payload
    )

    print(f"\n  [PUT NEGATIVE] Nonexistent user status: {resp.status_code}")
    print(f"  [PUT NEGATIVE] Body: {resp.json()}")
    print(
        "  [PUT NEGATIVE] NOTE: reqres.in simulates 200 for any ID. "
        "Real API should return 404 for nonexistent resource."
    )

    # Server must not crash
    assert resp.status_code != 500


# =============================================
# PATCH TESTS — Partial update
# =============================================

def test_patch_user_returns_200(api_client, base_url):
    """
    PATCH /api/users/2 with partial body returns 200.

    PATCH = partial update.
    You send ONLY the fields you want to change.
    Fields you omit remain unchanged.

    Key difference from PUT:
    - PUT: send all fields, everything else is reset
    - PATCH: send only changed fields, rest stays the same

    Practical example:
    User has: name, email, phone, address, role
    You want to update only job title.
    PATCH: send {job: "new title"} → only job changes
    PUT: send {job: "new title"} → email, phone, address ALL cleared
    """
    payload = {"job": "Principal SDET"}  # only updating job

    resp = api_client.patch(
        f"{base_url}/users/{VALID_USER_ID}",
        json=payload
    )

    assert resp.status_code == 200, (
        f"Expected 200, got {resp.status_code}"
    )

    body = resp.json()

    assert body["job"] == payload["job"], (
        f"Expected job '{payload['job']}', got '{body['job']}'"
    )
    assert "updatedAt" in body, (
        "PATCH response must contain updatedAt"
    )

    print(f"\n  [PATCH] Updated job to: {body['job']}")
    print(f"  [PATCH] Updated at: {body['updatedAt']}")


def test_patch_single_field_does_not_require_full_body(
    api_client, base_url
):
    """
    PATCH with only one field must succeed.
    If the server requires all fields for PATCH,
    it is incorrectly implementing PUT behaviour.

    This test catches that design error.
    """
    # Send only name — no job, no other fields
    payload = {"name": "Partial Update Only"}

    resp = api_client.patch(
        f"{base_url}/users/{VALID_USER_ID}",
        json=payload
    )

    assert resp.status_code == 200, (
        f"PATCH with single field should return 200, got {resp.status_code}. "
        f"Server may be incorrectly requiring full body."
    )

    body = resp.json()
    assert body["name"] == payload["name"]

    print(f"\n  [PATCH] Single field update succeeded")
    print(f"  [PATCH] Name: {body['name']}")


def test_patch_nonexistent_user(api_client, base_url):
    """
    PATCH to a nonexistent user ID.
    Same analysis as PUT nonexistent — documents behaviour.
    """
    payload = {"job": "Ghost Role"}

    resp = api_client.patch(
        f"{base_url}/users/9999",
        json=payload
    )

    print(
        f"\n  [PATCH NEGATIVE] Nonexistent user: {resp.status_code}"
    )
    print(f"  [PATCH NEGATIVE] Body: {resp.json()}")

    assert resp.status_code != 500


def test_put_vs_patch_both_return_updated_at(api_client, base_url):
    """
    Both PUT and PATCH must return updatedAt.
    This timestamp confirms the server processed the update.
    Missing updatedAt is a red flag — update may have been silently ignored.
    """
    put_resp = api_client.put(
        f"{base_url}/users/{VALID_USER_ID}",
        json={"name": "Test", "job": "Tester"}
    )
    patch_resp = api_client.patch(
        f"{base_url}/users/{VALID_USER_ID}",
        json={"job": "Tester"}
    )

    assert "updatedAt" in put_resp.json(), "PUT must return updatedAt"
    assert "updatedAt" in patch_resp.json(), "PATCH must return updatedAt"

    put_time = put_resp.json()["updatedAt"]
    patch_time = patch_resp.json()["updatedAt"]

    print(f"\n  [PUT vs PATCH] PUT updatedAt: {put_time}")
    print(f"  [PUT vs PATCH] PATCH updatedAt: {patch_time}")
    print("  [PUT vs PATCH] Both return updatedAt — correct")