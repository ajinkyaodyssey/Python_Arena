# week5/saturday_project/tests/api/test_auth.py
# Authentication flow tests — login, register, token usage

from .schemas import (
    LOGIN_RESPONSE_SCHEMA,
    REGISTER_RESPONSE_SCHEMA,
    ERROR_RESPONSE_SCHEMA,
    validate
)


class TestLogin:
    """POST /api/login — authentication endpoint."""

    def test_login_with_valid_credentials_returns_200(
        self, api, base_url
    ):
        resp = api.post(
            f"{base_url}/login",
            json={
                "email": "eve.holt@reqres.in",
                "password": "cityslicka"
            }
        )
        assert resp.status_code == 200

    def test_login_response_matches_schema(
        self, api, base_url
    ):
        resp = api.post(
            f"{base_url}/login",
            json={
                "email": "eve.holt@reqres.in",
                "password": "cityslicka"
            }
        )
        assert resp.status_code == 200
        validate(
            resp.json(),
            LOGIN_RESPONSE_SCHEMA,
            "POST /api/login"
        )

    def test_login_returns_non_empty_token(
        self, api, base_url
    ):
        resp = api.post(
            f"{base_url}/login",
            json={
                "email": "eve.holt@reqres.in",
                "password": "cityslicka"
            }
        )
        token = resp.json()["token"]
        assert isinstance(token, str)
        assert len(token) > 0

    def test_login_missing_password_returns_400(
        self, api, base_url
    ):
        resp = api.post(
            f"{base_url}/login",
            json={"email": "eve.holt@reqres.in"}
        )
        assert resp.status_code == 400
        validate(
            resp.json(),
            ERROR_RESPONSE_SCHEMA,
            "POST /api/login missing password"
        )

    def test_login_missing_email_returns_400(
        self, api, base_url
    ):
        resp = api.post(
            f"{base_url}/login",
            json={"password": "cityslicka"}
        )
        assert resp.status_code == 400

    def test_login_empty_body_returns_400(
        self, api, base_url
    ):
        resp = api.post(f"{base_url}/login", json={})
        assert resp.status_code == 400

    def test_login_error_response_has_error_field(
        self, api, base_url
    ):
        resp = api.post(
            f"{base_url}/login",
            json={"email": "eve.holt@reqres.in"}
        )
        assert resp.status_code == 400
        body = resp.json()
        assert "error" in body
        assert len(body["error"]) > 0

    def test_login_token_is_consistent_for_same_user(
        self, api, base_url
    ):
        """
        reqres.in returns same token for same user.
        Real JWT APIs return different tokens each login.
        """
        creds = {
            "email": "eve.holt@reqres.in",
            "password": "cityslicka"
        }
        resp1 = api.post(f"{base_url}/login", json=creds)
        resp2 = api.post(f"{base_url}/login", json=creds)
        assert resp1.json()["token"] == resp2.json()["token"]


class TestRegister:
    """POST /api/register — user registration endpoint."""

    def test_register_with_valid_data_returns_200(
        self, api, base_url
    ):
        resp = api.post(
            f"{base_url}/register",
            json={
                "email": "eve.holt@reqres.in",
                "password": "pistol"
            }
        )
        assert resp.status_code == 200

    def test_register_response_matches_schema(
        self, api, base_url
    ):
        resp = api.post(
            f"{base_url}/register",
            json={
                "email": "eve.holt@reqres.in",
                "password": "pistol"
            }
        )
        assert resp.status_code == 200
        validate(
            resp.json(),
            REGISTER_RESPONSE_SCHEMA,
            "POST /api/register"
        )

    def test_register_returns_id_and_token(
        self, api, base_url
    ):
        resp = api.post(
            f"{base_url}/register",
            json={
                "email": "eve.holt@reqres.in",
                "password": "pistol"
            }
        )
        body = resp.json()
        assert "id" in body and body["id"] > 0
        assert "token" in body and len(body["token"]) > 0

    def test_register_without_password_returns_400(
        self, api, base_url
    ):
        resp = api.post(
            f"{base_url}/register",
            json={"email": "sydney@fife"}
        )
        assert resp.status_code == 400
        assert "error" in resp.json()

    def test_register_without_email_returns_400(
        self, api, base_url
    ):
        resp = api.post(
            f"{base_url}/register",
            json={"password": "pistol"}
        )
        assert resp.status_code == 400


class TestAuthToken:
    """Token usage in subsequent requests."""

    def test_auth_token_fixture_provides_valid_token(
        self, auth_token
    ):
        assert isinstance(auth_token, str)
        assert len(auth_token) > 0

    def test_auth_api_fixture_has_authorization_header(
        self, auth_api
    ):
        assert "Authorization" in auth_api.headers
        assert auth_api.headers["Authorization"].startswith(
            "Bearer "
        )

    def test_authenticated_request_succeeds(
        self, auth_api, base_url
    ):
        resp = auth_api.get(f"{base_url}/users/2")
        assert resp.status_code == 200
