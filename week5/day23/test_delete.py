# week5/day23/test_delete.py
# DELETE /api/users/{id} tests — happy path + negative cases
# Run with: pytest week5/day23/test_delete.py -v -s

BASE_URL = "https://reqres.in/api"
VALID_USER_ID = 2


# =============================================
# HAPPY PATH — 3 tests
# =============================================

def test_delete_user_returns_204(api_client, base_url):
    """
    DELETE /api/users/2 must return 204 No Content.

    204 = success, nothing to return.
    This is the correct success code for DELETE.

    Wrong codes that should fail:
    - 200 with body: DELETE succeeded but returning body is unusual
    - 200 with empty body: technically wrong status for empty
    - 404: resource not found — delete failed

    What we verify:
    - Status is exactly 204
    - Body is empty (no content to return on DELETE)
    """
    resp = api_client.delete(
        f"{base_url}/users/{VALID_USER_ID}"
    )

    assert resp.status_code == 204, (
        f"Expected 204 No Content, got {resp.status_code}. "
        f"Body: {resp.text[:100]}"
    )

    # 204 must have empty body
    assert resp.text == "" or resp.text is None, (
        f"DELETE response body must be empty for 204, "
        f"got: '{resp.text[:100]}'"
    )

    print(f"\n  [DELETE] Status: {resp.status_code} No Content")
    print(f"  [DELETE] Body length: {len(resp.text)} (correct: 0)")


def test_delete_response_has_no_content_type(api_client, base_url):
    """
    204 No Content responses typically do not have Content-Type header
    because there is no content to describe.

    Some APIs include Content-Type even for 204 — that is acceptable.
    What is NOT acceptable: Content-Type claiming JSON when body is empty.

    This test documents actual header behaviour.
    """
    resp = api_client.delete(
        f"{base_url}/users/{VALID_USER_ID}"
    )

    assert resp.status_code == 204

    content_type = resp.headers.get("Content-Type", "")
    content_length = resp.headers.get("Content-Length", "0")

    print(f"\n  [DELETE HEADERS] Content-Type: '{content_type}'")
    print(f"  [DELETE HEADERS] Content-Length: '{content_length}'")

    # If Content-Type says JSON but body is empty that is inconsistent
    if "application/json" in content_type:
        # JSON Content-Type with empty body is inconsistent
        # But acceptable in some API implementations
        print(
            "  [DELETE HEADERS] NOTE: Content-Type=JSON but body is empty. "
            "Acceptable but inconsistent."
        )


def test_delete_response_time_under_2s(api_client, base_url):
    """
    DELETE must complete within 2 seconds.
    Slow deletes indicate cascade issues or missing indexes
    on foreign key relationships in the DB.
    """
    resp = api_client.delete(
        f"{base_url}/users/{VALID_USER_ID}"
    )

    assert resp.status_code == 204

    response_time = resp.elapsed.total_seconds()
    assert response_time < 2.0, (
        f"DELETE response time {response_time:.3f}s exceeded 2s"
    )

    print(f"\n  [DELETE PERF] Response time: {response_time:.3f}s")


# =============================================
# NEGATIVE CASES — 3 tests
# =============================================

def test_delete_nonexistent_user_returns_404(api_client, base_url):
    """
    DELETE /api/users/9999 — user does not exist.

    Expected behaviour on a real API: 404 Not Found.
    You cannot delete something that does not exist.

    Some APIs return 204 even for nonexistent resources
    (idempotent delete — calling DELETE multiple times
    has the same result as calling once: resource is gone).
    Both are valid API designs. Document which your API uses.

    reqres.in returns 204 for any ID — fully simulated.
    """
    resp = api_client.delete(f"{base_url}/users/9999")

    print(f"\n  [DELETE NEGATIVE] Nonexistent user: {resp.status_code}")
    print(f"  [DELETE NEGATIVE] Body: '{resp.text}'")
    print(
        "  [DELETE NEGATIVE] NOTE: reqres.in returns 204 for any ID. "
        "Real API should return 404 for nonexistent resource, "
        "OR 204 (idempotent delete). Document which your API uses."
    )

    # At minimum must not crash
    assert resp.status_code != 500
    # Should be 404 or 204 — not 200, not 400, not 500
    assert resp.status_code in [204, 404], (
        f"Expected 204 or 404 for nonexistent user, got {resp.status_code}"
    )


def test_delete_same_user_twice(api_client, base_url):
    """
    DELETE the same user twice.

    First call: 204 (deleted successfully)
    Second call: either
    - 404 (correct — resource no longer exists)
    - 204 (idempotent — deleting already-deleted is still success)

    Both are valid API designs.
    What is WRONG: 500 Internal Server Error on second delete.
    This would indicate the server crashes when trying to delete
    a resource that is already gone — a real production bug.

    reqres.in returns 204 for both — idempotent simulation.
    """
    first = api_client.delete(
        f"{base_url}/users/{VALID_USER_ID}"
    )
    second = api_client.delete(
        f"{base_url}/users/{VALID_USER_ID}"
    )

    assert first.status_code == 204, (
        f"First delete should be 204, got {first.status_code}"
    )

    # Second delete must not crash the server
    assert second.status_code != 500, (
        "Server must not return 500 on duplicate DELETE — server bug"
    )
    assert second.status_code in [204, 404], (
        f"Second delete should be 204 (idempotent) or 404 (not found), "
        f"got {second.status_code}"
    )

    print(f"\n  [DELETE NEGATIVE] First delete: {first.status_code}")
    print(f"  [DELETE NEGATIVE] Second delete: {second.status_code}")
    if second.status_code == 204:
        print("  [DELETE NEGATIVE] API is idempotent — 204 for both")
    else:
        print("  [DELETE NEGATIVE] API returns 404 for already-deleted resource")


def test_cannot_get_user_after_delete_on_real_api(
    api_client, base_url
):
    """
    On a REAL persistent API:
    DELETE user → GET that user → 404

    reqres.in does not persist — GET still returns 200 after DELETE.
    This test documents that gap explicitly.

    WHY THIS TEST EXISTS:
    Writing tests that document known API limitations is
    a real SDET skill. It tells the team exactly what is
    and is not covered by the test suite.
    """
    # DELETE the user
    delete_resp = api_client.delete(
        f"{base_url}/users/{VALID_USER_ID}"
    )
    assert delete_resp.status_code == 204

    # GET the same user — on reqres.in it STILL returns 200
    # because data is not actually deleted
    get_resp = api_client.get(
        f"{base_url}/users/{VALID_USER_ID}"
    )

    print(f"\n  [DELETE→GET] Delete status: {delete_resp.status_code}")
    print(f"  [DELETE→GET] GET after delete: {get_resp.status_code}")

    if get_resp.status_code == 200:
        print(
            "  [DELETE→GET] NOTE: reqres.in returns 200 after DELETE. "
            "Data is not persisted. "
            "On a real API this should return 404."
        )
        print(
            "  [DELETE→GET] This is a KNOWN LIMITATION of reqres.in, "
            "not a test failure."
        )
    elif get_resp.status_code == 404:
        print(
            "  [DELETE→GET] Real delete behaviour confirmed — "
            "404 after DELETE."
        )

    # The test passes regardless — it is a documentation test
    assert get_resp.status_code in [200, 404], (
        f"Expected 200 (simulated) or 404 (real), got {get_resp.status_code}"
    )
