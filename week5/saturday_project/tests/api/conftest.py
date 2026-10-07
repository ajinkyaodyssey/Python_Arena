# week5/saturday_project/tests/api/conftest.py
import pytest
import requests
import os
import logging
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger(__name__)

BASE_URL = "https://reqres.in/api"
VALID_EMAIL = "eve.holt@reqres.in"
VALID_PASSWORD = "cityslicka"


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL


@pytest.fixture(scope="session")
def api():
    """
    Authenticated requests.Session.
    x-api-key header applied to every request automatically.
    Session-scoped: one connection pool for the entire run.
    """
    key = os.getenv("REQRES_API_KEY", "")
    if not key:
        pytest.skip(
            "REQRES_API_KEY not set. "
            "Add to .env file. See .env.example."
        )

    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json",
        "x-api-key": key
    })
    log.info(f"API session created. Key: {key[:4]}****")
    yield session
    session.close()


@pytest.fixture(scope="session")
def auth_token(api, base_url) -> str:
    """Login once, return token for all auth tests."""
    resp = api.post(
        f"{base_url}/login",
        json={"email": VALID_EMAIL, "password": VALID_PASSWORD}
    )
    assert resp.status_code == 200, (
        f"Login failed: {resp.status_code} {resp.text[:100]}"
    )
    token = resp.json()["token"]
    log.info(f"Auth token obtained: {token[:8]}...")
    return token


@pytest.fixture(scope="session")
def auth_api(api, auth_token) -> requests.Session:
    """Authenticated session with Bearer token."""
    api.headers["Authorization"] = f"Bearer {auth_token}"
    return api
