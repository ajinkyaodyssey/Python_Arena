# week5/saturday_project/tests/api/test_users_get.py
# GET endpoint tests for /api/users
# Coverage: single user, list users, pagination, edge cases

import math
from .schemas import (
    SINGLE_USER_RESPONSE_SCHEMA,
    LIST_USERS_RESPONSE_SCHEMA,
    USER_OBJECT_SCHEMA,
    validate
)


class TestGetSingleUser:
    """GET /api/users/{id} — single user retrieval."""

    def test_get_existing_user_returns_200(self, api, base_url):
        resp = api.get(f"{base_url}/users/2")
        assert resp.status_code == 200, (
            f"Expected 200, got {resp.status_code}"
        )

    def test_get_existing_user_response_matches_schema(
        self, api, base_url
    ):
        resp = api.get(f"{base_url}/users/2")
        assert resp.status_code == 200
        validate(
            resp.json(),
            SINGLE_USER_RESPONSE_SCHEMA,
            "GET /api/users/2"
        )

    def test_get_existing_user_returns_correct_data(
        self, api, base_url
    ):
        resp = api.get(f"{base_url}/users/2")
        data = resp.json()["data"]

        assert data["id"] == 2
        assert data["email"] == "janet.weaver@reqres.in"
        assert data["first_name"] == "Janet"
        assert data["last_name"] == "Weaver"

    def test_get_user_avatar_is_valid_https_url(
        self, api, base_url
    ):
        resp = api.get(f"{base_url}/users/2")
        avatar = resp.json()["data"]["avatar"]

        assert avatar.startswith("https://"), (
            f"Avatar must be HTTPS, got: {avatar}"
        )
        assert len(avatar) > 10

    def test_get_user_response_time_under_2s(
        self, api, base_url
    ):
        resp = api.get(f"{base_url}/users/2")
        elapsed = resp.elapsed.total_seconds()
        assert elapsed < 2.0, (
            f"Response time {elapsed:.3f}s exceeded 2s threshold"
        )

    def test_get_user_content_type_is_json(
        self, api, base_url
    ):
        resp = api.get(f"{base_url}/users/2")
        assert "application/json" in resp.headers.get(
            "Content-Type", ""
        )

    def test_get_nonexistent_user_returns_404(
        self, api, base_url
    ):
        resp = api.get(f"{base_url}/users/9999")
        assert resp.status_code == 404, (
            f"Expected 404 for missing user, got {resp.status_code}"
        )

    def test_get_nonexistent_user_returns_empty_body(
        self, api, base_url
    ):
        resp = api.get(f"{base_url}/users/9999")
        assert resp.status_code == 404
        assert resp.json() == {}, (
            f"Expected empty body for 404, got: {resp.json()}"
        )

    def test_get_user_with_id_zero_returns_404(
        self, api, base_url
    ):
        """ID 0 should not be a valid user — document behaviour."""
        resp = api.get(f"{base_url}/users/0")
        assert resp.status_code in [404, 400], (
            f"ID 0 should return 404 or 400, got {resp.status_code}"
        )

    def test_get_multiple_different_users_return_correct_ids(
        self, api, base_url
    ):
        """Each user endpoint returns data for the correct user."""
        for user_id in [1, 2, 3]:
            resp = api.get(f"{base_url}/users/{user_id}")
            assert resp.status_code == 200
            assert resp.json()["data"]["id"] == user_id, (
                f"GET /users/{user_id} returned wrong id: "
                f"{resp.json()['data']['id']}"
            )


class TestListUsers:
    """GET /api/users — paginated user list."""

    def test_list_users_returns_200(self, api, base_url):
        resp = api.get(f"{base_url}/users", params={"page": 1})
        assert resp.status_code == 200

    def test_list_users_response_matches_schema(
        self, api, base_url
    ):
        resp = api.get(f"{base_url}/users", params={"page": 1})
        assert resp.status_code == 200
        validate(
            resp.json(),
            LIST_USERS_RESPONSE_SCHEMA,
            "GET /api/users?page=1"
        )

    def test_list_users_data_count_matches_per_page(
        self, api, base_url
    ):
        resp = api.get(f"{base_url}/users", params={"page": 1})
        body = resp.json()
        assert len(body["data"]) == body["per_page"], (
            f"Expected {body['per_page']} users, "
            f"got {len(body['data'])}"
        )

    def test_list_users_total_pages_math_is_correct(
        self, api, base_url
    ):
        resp = api.get(f"{base_url}/users", params={"page": 1})
        body = resp.json()
        expected = math.ceil(body["total"] / body["per_page"])
        assert body["total_pages"] == expected, (
            f"total_pages {body['total_pages']} != "
            f"ceil({body['total']}/{body['per_page']})={expected}"
        )

    def test_list_users_each_user_matches_schema(
        self, api, base_url
    ):
        resp = api.get(f"{base_url}/users", params={"page": 1})
        users = resp.json()["data"]
        errors = []
        for i, user in enumerate(users):
            try:
                validate(
                    user, USER_OBJECT_SCHEMA,
                    f"user index {i} id={user.get('id')}"
                )
            except AssertionError as e:
                errors.append(str(e)[:100])
        assert not errors, (
            f"Schema errors in {len(errors)} users:\n"
            + "\n".join(errors)
        )

    def test_list_users_page_2_returns_different_users(
        self, api, base_url
    ):
        resp1 = api.get(f"{base_url}/users", params={"page": 1})
        resp2 = api.get(f"{base_url}/users", params={"page": 2})
        assert resp1.status_code == 200
        assert resp2.status_code == 200

        ids1 = {u["id"] for u in resp1.json()["data"]}
        ids2 = {u["id"] for u in resp2.json()["data"]}
        overlap = ids1 & ids2

        assert not overlap, (
            f"Pages 1 and 2 share user IDs: {overlap}"
        )

    def test_list_users_all_emails_are_valid(
        self, api, base_url
    ):
        resp = api.get(f"{base_url}/users", params={"page": 1})
        users = resp.json()["data"]
        for user in users:
            email = user["email"]
            assert "@" in email and "." in email.split("@")[1], (
                f"Invalid email for user {user['id']}: {email}"
            )

    def test_list_users_response_time_under_2s(
        self, api, base_url
    ):
        resp = api.get(f"{base_url}/users", params={"page": 1})
        assert resp.elapsed.total_seconds() < 2.0
