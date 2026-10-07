# week5/saturday_project/tests/api/test_users_write.py
# POST, PUT, PATCH, DELETE tests for /api/users

import time
import uuid
from .schemas import (
    CREATE_USER_RESPONSE_SCHEMA,
    UPDATE_USER_RESPONSE_SCHEMA,
    validate
)


class TestCreateUser:
    """POST /api/users — create a new user."""

    def test_create_user_returns_201(self, api, base_url):
        resp = api.post(
            f"{base_url}/users",
            json={"name": "Divya Kumar", "job": "SDET"}
        )
        assert resp.status_code == 201

    def test_create_user_response_matches_schema(
        self, api, base_url
    ):
        resp = api.post(
            f"{base_url}/users",
            json={"name": "Divya Kumar", "job": "SDET"}
        )
        assert resp.status_code == 201
        validate(
            resp.json(),
            CREATE_USER_RESPONSE_SCHEMA,
            "POST /api/users"
        )

    def test_create_user_response_contains_server_assigned_id(
        self, api, base_url
    ):
        resp = api.post(
            f"{base_url}/users",
            json={"name": "Test User", "job": "Tester"}
        )
        body = resp.json()
        assert "id" in body
        assert body["id"] is not None
        assert len(str(body["id"])) > 0

    def test_create_user_response_contains_created_at_timestamp(
        self, api, base_url
    ):
        resp = api.post(
            f"{base_url}/users",
            json={"name": "Test User", "job": "Tester"}
        )
        body = resp.json()
        assert "createdAt" in body
        assert len(body["createdAt"]) > 0

    def test_create_user_response_reflects_sent_name(
        self, api, base_url
    ):
        unique_name = f"User_{uuid.uuid4().hex[:8]}"
        resp = api.post(
            f"{base_url}/users",
            json={"name": unique_name, "job": "SDET"}
        )
        assert resp.json()["name"] == unique_name

    def test_create_user_response_reflects_sent_job(
        self, api, base_url
    ):
        unique_job = f"Role_{uuid.uuid4().hex[:8]}"
        resp = api.post(
            f"{base_url}/users",
            json={"name": "Test User", "job": unique_job}
        )
        assert resp.json()["job"] == unique_job

    def test_create_user_with_empty_body_does_not_crash(
        self, api, base_url
    ):
        """
        Empty body — real API should return 400.
        reqres.in accepts it (no validation).
        Document behaviour. Server must not return 500.
        """
        resp = api.post(f"{base_url}/users", json={})
        assert resp.status_code != 500, (
            "Server must not crash on empty body"
        )

    def test_create_user_response_time_under_2s(
        self, api, base_url
    ):
        resp = api.post(
            f"{base_url}/users",
            json={"name": "Perf Test", "job": "Tester"}
        )
        assert resp.elapsed.total_seconds() < 2.0


class TestUpdateUser:
    """PUT and PATCH /api/users/{id} — update existing user."""

    def test_put_user_returns_200(self, api, base_url):
        time.sleep(1)
        resp = api.put(
            f"{base_url}/users/2",
            json={"name": "Janet Updated", "job": "Senior Engineer"}
        )
        assert resp.status_code == 200

    def test_put_user_response_matches_schema(
        self, api, base_url
    ):
        time.sleep(1)
        resp = api.put(
            f"{base_url}/users/2",
            json={"name": "Janet Updated", "job": "Senior Engineer"}
        )
        assert resp.status_code == 200
        validate(
            resp.json(),
            UPDATE_USER_RESPONSE_SCHEMA,
            "PUT /api/users/2"
        )

    def test_put_user_response_reflects_sent_data(
        self, api, base_url
    ):
        time.sleep(1)
        unique_name = f"PUT_{uuid.uuid4().hex[:8]}"
        unique_job = f"Job_{uuid.uuid4().hex[:8]}"
        resp = api.put(
            f"{base_url}/users/2",
            json={"name": unique_name, "job": unique_job}
        )
        assert resp.json()["name"] == unique_name
        assert resp.json()["job"] == unique_job

    def test_put_user_response_has_updated_at(
        self, api, base_url
    ):
        time.sleep(1)
        resp = api.put(
            f"{base_url}/users/2",
            json={"name": "Test", "job": "Tester"}
        )
        assert "updatedAt" in resp.json()
        assert len(resp.json()["updatedAt"]) > 0

    def test_patch_user_returns_200(self, api, base_url):
        time.sleep(1)
        resp = api.patch(
            f"{base_url}/users/2",
            json={"job": "Principal SDET"}
        )
        assert resp.status_code == 200

    def test_patch_user_response_matches_schema(
        self, api, base_url
    ):
        time.sleep(1)
        resp = api.patch(
            f"{base_url}/users/2",
            json={"name": "Janet", "job": "Principal SDET"}
        )
        assert resp.status_code == 200
        validate(
            resp.json(),
            UPDATE_USER_RESPONSE_SCHEMA,
            "PATCH /api/users/2"
        )

    def test_patch_user_with_single_field_succeeds(
        self, api, base_url
    ):
        """PATCH should not require full body like PUT."""
        time.sleep(1)
        resp = api.patch(
            f"{base_url}/users/2",
            json={"job": "Updated Role Only"}
        )
        assert resp.status_code == 200, (
            f"PATCH with single field should succeed, "
            f"got {resp.status_code}"
        )

    def test_patch_user_has_updated_at(self, api, base_url):
        time.sleep(1)
        resp = api.patch(
            f"{base_url}/users/2",
            json={"name": "Test", "job": "Tester"}
        )
        assert "updatedAt" in resp.json()


class TestDeleteUser:
    """DELETE /api/users/{id} — remove a user."""

    def test_delete_user_returns_204(self, api, base_url):
        resp = api.delete(f"{base_url}/users/2")
        assert resp.status_code == 204, (
            f"Expected 204 No Content, got {resp.status_code}"
        )

    def test_delete_user_response_body_is_empty(
        self, api, base_url
    ):
        resp = api.delete(f"{base_url}/users/2")
        assert resp.status_code == 204
        assert resp.text == "", (
            f"DELETE 204 body must be empty, got: '{resp.text[:50]}'"
        )

    def test_delete_user_response_time_under_2s(
        self, api, base_url
    ):
        resp = api.delete(f"{base_url}/users/2")
        assert resp.elapsed.total_seconds() < 2.0

    def test_delete_nonexistent_user_does_not_crash(
        self, api, base_url
    ):
        """
        DELETE nonexistent user.
        Real API: 404. reqres.in: 204 (fully simulated).
        Must not return 500.
        """
        resp = api.delete(f"{base_url}/users/9999")
        assert resp.status_code != 500
        assert resp.status_code in [204, 404], (
            f"Expected 204 or 404, got {resp.status_code}"
        )

    def test_delete_same_user_twice_does_not_crash(
        self, api, base_url
    ):
        """
        Double DELETE must not crash.
        reqres.in: 204 for both (idempotent simulation).
        Real API: 204 then 404.
        """
        first = api.delete(f"{base_url}/users/2")
        second = api.delete(f"{base_url}/users/2")
        assert first.status_code == 204
        assert second.status_code != 500
        assert second.status_code in [204, 404]
