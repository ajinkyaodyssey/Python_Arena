# week5/saturday_project/tests/api/test_edge_cases.py
# Edge cases and boundary conditions.
# These are the tests that separate good SDET suites from basic ones.

import time
from .schemas import (
    LIST_USERS_RESPONSE_SCHEMA,
    validate
)


class TestDelayedResponse:
    """GET /api/users?delay=N — simulated slow responses."""

    def test_delayed_response_still_returns_correct_data(
        self, api, base_url
    ):
        """
        reqres.in supports ?delay=N to simulate slow responses.
        Data must still be correct even when response is slow.
        Tests that timeout handling does not corrupt the response.
        """
        resp = api.get(
            f"{base_url}/users",
            params={"delay": 2},
            timeout=10
        )
        assert resp.status_code == 200
        validate(
            resp.json(),
            LIST_USERS_RESPONSE_SCHEMA,
            "GET /api/users?delay=2"
        )

    def test_delayed_response_takes_expected_time(
        self, api, base_url
    ):
        """
        Response with delay=2 should take at least 2 seconds.
        Verifies the delay parameter is actually applied.
        """
        start = time.perf_counter()
        resp = api.get(
            f"{base_url}/users",
            params={"delay": 2},
            timeout=10
        )
        elapsed = time.perf_counter() - start

        assert resp.status_code == 200
        assert elapsed >= 2.0, (
            f"Expected at least 2s with delay=2, "
            f"got {elapsed:.2f}s"
        )


class TestPaginationEdgeCases:
    """Pagination boundary conditions."""

    def test_page_beyond_total_returns_empty_data(
        self, api, base_url
    ):
        """
        Requesting a page beyond total_pages should return
        empty data array, not 404 or 500.
        """
        resp = api.get(
            f"{base_url}/users",
            params={"page": 9999}
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body
        assert isinstance(body["data"], list)
        assert len(body["data"]) == 0, (
            f"Page 9999 should be empty, got {len(body['data'])} users"
        )

    def test_per_page_parameter_respected(
        self, api, base_url
    ):
        """
        ?per_page=3 should return exactly 3 users.
        Tests that the per_page parameter is actually applied.
        """
        resp = api.get(
            f"{base_url}/users",
            params={"page": 1, "per_page": 3}
        )
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["data"]) == 3, (
            f"Expected 3 users with per_page=3, "
            f"got {len(body['data'])}"
        )
        assert body["per_page"] == 3


class TestDataIntegrity:
    """Data consistency checks across endpoints."""

    def test_user_ids_in_list_are_unique(
        self, api, base_url
    ):
        """No duplicate IDs should appear in a page of results."""
        resp = api.get(f"{base_url}/users", params={"page": 1})
        users = resp.json()["data"]
        ids = [u["id"] for u in users]
        assert len(ids) == len(set(ids)), (
            f"Duplicate IDs found in list response: {ids}"
        )

    def test_user_ids_are_sequential_within_page(
        self, api, base_url
    ):
        """
        IDs on page 1 should be lower than IDs on page 2.
        Tests that pagination returns ordered, non-overlapping data.
        """
        resp1 = api.get(f"{base_url}/users", params={"page": 1})
        resp2 = api.get(f"{base_url}/users", params={"page": 2})

        max_id_page1 = max(u["id"] for u in resp1.json()["data"])
        min_id_page2 = min(u["id"] for u in resp2.json()["data"])

        assert max_id_page1 < min_id_page2, (
            f"Page 1 max ID {max_id_page1} should be less than "
            f"page 2 min ID {min_id_page2}"
        )

    def test_all_users_have_non_empty_names(
        self, api, base_url
    ):
        resp = api.get(f"{base_url}/users", params={"page": 1})
        users = resp.json()["data"]
        for user in users:
            assert user["first_name"].strip(), (
                f"User {user['id']} has empty first_name"
            )
            assert user["last_name"].strip(), (
                f"User {user['id']} has empty last_name"
            )

    def test_all_user_emails_contain_at_symbol(
        self, api, base_url
    ):
        resp = api.get(f"{base_url}/users", params={"page": 1})
        users = resp.json()["data"]
        for user in users:
            assert "@" in user["email"], (
                f"User {user['id']} email missing @: {user['email']}"
            )

    def test_single_user_data_matches_list_data(
        self, api, base_url
    ):
        """
        GET /users/2 data must match the entry for user 2
        in GET /users list. Consistency check between endpoints.
        """
        single_resp = api.get(f"{base_url}/users/2")
        list_resp = api.get(f"{base_url}/users", params={"page": 1})

        single_user = single_resp.json()["data"]
        list_users = list_resp.json()["data"]

        list_user_2 = next(
            (u for u in list_users if u["id"] == 2), None
        )
        assert list_user_2 is not None, (
            "User 2 not found in list response"
        )

        assert single_user["email"] == list_user_2["email"], (
            f"Email mismatch: single={single_user['email']}, "
            f"list={list_user_2['email']}"
        )
        assert single_user["first_name"] == list_user_2["first_name"]
        assert single_user["last_name"] == list_user_2["last_name"]


class TestContentNegotiation:
    """HTTP headers and content type handling."""

    def test_response_content_type_is_json_for_all_gets(
        self, api, base_url
    ):
        endpoints = [
            f"{base_url}/users/2",
            f"{base_url}/users?page=1",
        ]
        for url in endpoints:
            resp = api.get(url)
            content_type = resp.headers.get("Content-Type", "")
            assert "application/json" in content_type, (
                f"Expected JSON Content-Type for {url}, "
                f"got: {content_type}"
            )

    def test_all_responses_are_valid_json(
        self, api, base_url
    ):
        """Every endpoint must return parseable JSON."""
        endpoints = [
            f"{base_url}/users/2",
            f"{base_url}/users?page=1",
        ]
        for url in endpoints:
            resp = api.get(url)
            try:
                body = resp.json()
                assert isinstance(body, dict), (
                    f"Expected dict response from {url}"
                )
            except Exception as e:
                raise AssertionError(
                    f"Response from {url} is not valid JSON: {e}"
                )
