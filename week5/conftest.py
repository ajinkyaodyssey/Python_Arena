# week5/conftest.py
# Shared fixtures for ALL week5 API tests.
# Lives at week5/ level so it applies to all subdirectories.
#
# WHY THIS FILE EXISTS:
# reqres.in now requires x-api-key header on all endpoints.
# Rather than updating every day's conftest separately,
# we define api_client once here and all subdirectories inherit it.
# This is the correct pytest pattern — shared fixtures at the
# highest relevant directory level.

import pytest
import requests
import os
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()

BASE_URL = "https://reqres.in/api"


@pytest.fixture(scope="session")
def base_url() -> str:
    """Base URL for all reqres.in API calls."""
    return BASE_URL


@pytest.fixture(scope="session")
def api_client():
    """
    Session-scoped authenticated HTTP client.

    Includes x-api-key header required by reqres.in since 2026.
    Key is loaded from .env file — never hardcoded in source.

    Why Session():
    - Connection pooling: reuses TCP connections across requests
    - Shared headers: set once, applied to every request
    - Shared cookies: essential for stateful auth flows
    - Mirrors real user session behaviour

    Why session scope:
    - Creating a session is cheap but login/auth state is expensive
    - All tests in the run share one session safely
    - Headers are read-only after setup — no test pollution
    """
    api_key = os.getenv("REQRES_API_KEY", "")

    if not api_key:
        pytest.skip(
            "REQRES_API_KEY not set in .env file. "
            "Get your free key at app.reqres.in/api-keys"
        )

    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json",
        "x-api-key": api_key
    })

    yield session
    session.close()


@pytest.fixture(scope="session")
def valid_credentials() -> dict:
    """Valid login credentials for reqres.in test account."""
    return {
        "email": "eve.holt@reqres.in",
        "password": "cityslicka"
    }


@pytest.fixture(scope="session")
def invalid_credentials() -> dict:
    """Invalid credentials for negative login tests."""
    return {
        "email": "invalid@reqres.in",
        "password": "wrongpassword"
    }