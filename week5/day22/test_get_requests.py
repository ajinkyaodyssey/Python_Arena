# week5/day22/test_get_requests.py
# 5 GET tests against reqres.in
# Covers: valid user, nonexistent user, pagination,
#         response time, Content-Type header
# Run with: pytest week5/day22/test_get_requests.py -v -s

from week5.day24.schemas import (
    SINGLE_USER_RESPONSE_SCHEMA,
    LIST_USERS_RESPONSE_SCHEMA,
    validate_schema
)

BASE_URL = "https://reqres.in/api"


# =============================================
# UNDERSTAND THE RESPONSE FIRST
# =============================================
# Before writing tests, know exactly what reqres.in returns.
#
# GET /api/users/2 returns:
# {
#   "data": {
#     "id": 2,
#     "email": "janet.weaver@reqres.in",
#     "first_name": "Janet",
#     "last_name": "Weaver",
#     "avatar": "https://reqres.in/img/faces/2-image.jpg"
#   },
#   "support": {
#     "url": "https://reqres.in/#support-heading",
#     "text": "To keep ReqRes free..."
#   }
# }
#
# GET /api/users?page=2 returns:
# {
#   "page": 2,
#   "per_page": 6,
#   "total": 12,
#   "total_pages": 2,
#   "data": [...6 user objects...],
#   "support": {...}
# }


# =============================================
# TEST 1: Valid user returns 200 with correct data
# =============================================

def test_get_valid_user_returns_200(api_client, base_url):
    """
    GET /api/users/2 should return 200 with user data.

    What we verify:
    - Status code is exactly 200 (not 201, not 204)
    - Response body has the expected structure
    - User data contains the correct values for user ID 2
    - Response headers confirm JSON content type

    This is the happy path — the most fundamental test.
    If this fails, every other test is meaningless.
    """
    resp = api_client.get(f"{base_url}/users/2")

    # Status code
    assert resp.status_code == 200, (
        f"Expected 200, got {resp.status_code}. "
        f"Body: {resp.text[:200]}"
    )

    validate_schema(
        resp.json(),
        SINGLE_USER_RESPONSE_SCHEMA,
        "GET /api/users/2"
    )

    # Parse response body
    body = resp.json()

    # Top-level structure
    assert "data" in body, f"Response missing 'data' key. Got: {list(body.keys())}"
    assert "support" in body, "Response missing 'support' key"

    # User data values
    data = body["data"]
    assert data["id"] == 2, f"Expected id=2, got {data['id']}"
    assert data["email"] == "janet.weaver@reqres.in", (
        f"Unexpected email: {data['email']}"
    )
    assert data["first_name"] == "Janet"
    assert data["last_name"] == "Weaver"
    assert "avatar" in data, "User should have an avatar URL"
    assert data["avatar"].startswith("https://"), (
        f"Avatar URL should start with https://, got: {data['avatar']}"
    )

    print(f"\n  [GET] User 2: {data['first_name']} {data['last_name']}")
    print(f"  [GET] Email: {data['email']}")
    
    
def test_get_valid_user_response_fields_are_correct_types(
    api_client, base_url
):
    """
    Every field must be the correct type.
    Status code 200 with a broken type (id as string) would
    pass a naive status-code-only check but break API consumers.

    This is schema validation without jsonschema library —
    pure Python type checking.
    """
    resp = api_client.get(f"{base_url}/users/2")
    data = resp.json()["data"]

    assert isinstance(data["id"], int), (
        f"id should be int, got {type(data['id']).__name__}"
    )
    assert isinstance(data["email"], str), (
        f"email should be str, got {type(data['email']).__name__}"
    )
    assert isinstance(data["first_name"], str)
    assert isinstance(data["last_name"], str)
    assert isinstance(data["avatar"], str)

    print(f"\n  [TYPES] id={type(data['id']).__name__}, "
          f"email={type(data['email']).__name__}")
    
    
# =============================================
# TEST 2: Nonexistent user returns 404
# =============================================

def test_get_nonexistent_user_returns_404(api_client, base_url):
    """
    GET /api/users/9999 — user does not exist.

    What we verify:
    - Status code is 404 Not Found
    - Response body is empty or minimal
      (reqres.in returns {} for 404)
    - We do NOT raise_for_status() here because 404 is the
      expected outcome — we want to verify it, not avoid it

    This is critical: a missing 404 handling in the app means
    the UI might crash or show stale data instead of "user not found"
    """
    resp = api_client.get(f"{base_url}/users/9999")

    assert resp.status_code == 404, (
        f"Expected 404 for nonexistent user, got {resp.status_code}"
    )

    # reqres.in returns empty object for 404
    body = resp.json()
    assert body == {}, (
        f"Expected empty body for 404, got: {body}"
    )

    print(f"\n  [404] Status: {resp.status_code}")
    print(f"  [404] Body: {resp.json()}")
    
    
def test_get_nonexistent_user_does_not_crash_server(
    api_client, base_url
):
    """
    A 404 is correct behaviour.
    A 500 for a missing resource is a server bug.

    This test explicitly verifies the server handles
    the missing resource gracefully, not by crashing.
    """
    # Try multiple nonexistent IDs
    nonexistent_ids = [0, 9999, 99999, -1]

    for user_id in nonexistent_ids:
        resp = api_client.get(f"{base_url}/users/{user_id}")
        assert resp.status_code != 500, (
            f"Server returned 500 for user_id={user_id} — server bug"
        )
        assert resp.status_code in [404, 400], (
            f"Expected 404 or 400 for user_id={user_id}, "
            f"got {resp.status_code}"
        )
        print(f"  [404] user_id={user_id} -> {resp.status_code} (correct)")
    
    
# =============================================
# TEST 3: List users with pagination
# =============================================

def test_list_users_returns_paginated_data(api_client, base_url):
    """
    GET /api/users?page=1 returns the first page of users.

    What we verify:
    - Status code 200
    - Pagination metadata is present and correct type
    - Data array contains exactly per_page items
    - Each user object has required fields

    Pagination is one of the most common API bugs.
    Testing it verifies:
    - The page parameter is actually used
    - Total and total_pages are calculated correctly
    - The data array has the right number of items
    """
    resp = api_client.get(f"{base_url}/users", params={"page": 1})

    assert resp.status_code == 200

    validate_schema(
        resp.json(), 
        LIST_USERS_RESPONSE_SCHEMA, 
        "GET /api/users?page=1"
    )

    body = resp.json()

    # Pagination metadata must exist
    assert "page" in body
    assert "per_page" in body
    assert "total" in body
    assert "total_pages" in body
    assert "data" in body
    
    # Metadata values and types
    assert body["page"] == 1, (
        f"Expected page=1, got {body['page']}"
    )
    assert isinstance(body["per_page"], int)
    assert isinstance(body["total"], int)
    assert isinstance(body["total_pages"], int)
    
    # Data array length matches per_page
    assert len(body["data"]) == body["per_page"], (
        f"Expected {body['per_page']} users, got {len(body['data'])}"
    )
    
    # Total pages calculation is mathematically correct
    import math
    expected_total_pages = math.ceil(
        body["total"] / body["per_page"]
    )
    assert body["total_pages"] == expected_total_pages, (
        f"total_pages={body['total_pages']} does not match "
        f"math.ceil({body['total']}/{body['per_page']})={expected_total_pages}"
    )

    # Each user has required fields
    required_fields = {"id", "email", "first_name", "last_name", "avatar"}
    for user in body["data"]:
        missing = required_fields - set(user.keys())
        assert not missing, (
            f"User {user.get('id')} missing fields: {missing}"
        )
    # 1. required_fields: The exact keys that must be present in every user object.
    # 2. set(user.keys()): Converts the API response keys into a mathematical set.
    # 3. Set Subtraction (-): 'required_fields - set(user.keys())' finds any 
    #    mandatory fields that the API failed to return. If 'missing' is 
    #    non-empty, the test fails.
    
    print(f"\n  [PAGINATION] Page: {body['page']}/{body['total_pages']}")
    print(f"  [PAGINATION] Users per page: {body['per_page']}")
    print(f"  [PAGINATION] Total users: {body['total']}")
    print(f"  [PAGINATION] Users on this page: {len(body['data'])}")
    
    
def test_different_pages_return_different_users(api_client, base_url):
    """
    Page 1 and page 2 must return different users.
    This verifies pagination is actually working —
    not just returning the same data for every page number.
    """
    resp1 = api_client.get(f"{base_url}/users", params={"page": 1})
    resp2 = api_client.get(f"{base_url}/users", params={"page": 2})
    
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    
    # Extract the "id" from each user and store all IDs in a set -> {....} => set comprehension (when there's a for)
    ids_page1 = {user["id"] for user in resp1.json()["data"]}       # {something for item in collection}
    ids_page2 = {user["id"] for user in resp2.json()["data"]}
    
    # No overlap between pages
    # Find the common IDs that are present in both page 1 and page 2.
    # The '&' operator performs a set intersection, returning only the IDs
    # that appear in both sets.
    overlap = ids_page1 & ids_page2
    assert not overlap, (
        f"Pages 1 and 2 share user IDs: {overlap}"
    )
    
    print(f"\n  [PAGINATION] Page 1 IDs: {sorted(ids_page1)}")      # sorted() does not modify ids_page1. It creates and returns a new sorted list.
    print(f"  [PAGINATION] Page 2 IDs: {sorted(ids_page2)}")
    print(f"  [PAGINATION] Overlap: {overlap} (correct: empty)")
    
    
# =============================================
# TEST 4: Response time under 2 seconds
# =============================================

def test_get_user_response_time_under_2s(api_client, base_url):
    """
    API response must arrive within 2 seconds.

    Why this matters:
    - Slow APIs degrade user experience
    - A response time spike can indicate a server issue
    - SLAs (Service Level Agreements) often specify max response times

    What we measure:
    - resp.elapsed is a timedelta object
    - .total_seconds() converts to float
    - We measure end-to-end: request sent to response received

    2 seconds is generous for reqres.in.
    In a real project, 200ms might be the threshold.
    Adjust based on the SLA for your specific API.
    """
    resp = api_client.get(f"{base_url}/users/2")
    
    assert resp.status_code == 200

    response_time = resp.elapsed.total_seconds()

    assert response_time < 2.0, (
        f"Response time {response_time:.3f}s exceeded 2s threshold. "
        f"This may indicate a server performance issue."
    )

    print(f"\n  [PERF] Response time: {response_time:.3f}s")
    print("  [PERF] Threshold: 2.000s")
    print(f"  [PERF] Status: {'PASS' if response_time < 2.0 else 'FAIL'}")
    

def test_list_users_response_time_under_2s(api_client, base_url):
    """
    List endpoint with pagination should also be fast.
    List endpoints often do more DB work than single-resource endpoints.
    """
    resp = api_client.get(
        f"{base_url}/users", params={"page": 1}
    )

    response_time = resp.elapsed.total_seconds()

    assert response_time < 2.0, (
        f"List response time {response_time:.3f}s exceeded 2s"
    )

    print(f"\n  [PERF] List response time: {response_time:.3f}s")


# =============================================
# TEST 5: Content-Type header verification
# =============================================

def test_get_user_content_type_is_json(api_client, base_url):
    """
    Response Content-Type must be application/json.

    Why headers matter:
    - Content-Type tells the client how to parse the body
    - If a JSON endpoint returns text/html, your resp.json() crashes
    - Header validation catches infrastructure misconfigurations
      (e.g., a reverse proxy returning HTML error pages instead of API responses)

    Note: Content-Type often includes charset:
    "application/json; charset=utf-8"
    We use 'in' not '==' to handle this correctly.
    """
    resp = api_client.get(f"{base_url}/users/2")

    assert resp.status_code == 200

    content_type = resp.headers.get("Content-Type", "")

    assert "application/json" in content_type, (
        f"Expected Content-Type to contain 'application/json', "
        f"got: '{content_type}'"
    )

    print(f"\n  [HEADERS] Content-Type: {content_type}")
    

def test_response_headers_contain_expected_keys(
    api_client, base_url
):
    """
    Verify the response has all headers the client depends on.

    Different from body validation — this checks the envelope,
    not the content. Missing headers can break:
    - CORS (Access-Control-Allow-Origin)
    - Caching (Cache-Control)
    - Rate limiting info (X-RateLimit-Remaining)
    """
    resp = api_client.get(f"{base_url}/users/2")

    headers = resp.headers

    # Content-Type must always be present
    assert "Content-Type" in headers, "Missing Content-Type header"

    # Content-Type must indicate JSON
    assert "application/json" in headers["Content-Type"]

    print("\n  [HEADERS] All response headers:")
    for key, value in headers.items():
        print(f"    {key}: {value}")
