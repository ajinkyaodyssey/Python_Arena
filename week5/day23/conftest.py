# week5/day23/conftest.py
import pytest
import requests

BASE_URL = "https://reqres.in/api"


@pytest.fixture(scope="session")
def api_client():
    """
    Session-scoped requests.Session.
    Headers set once, reused across all tests in the session.
    Connection pooling makes sequential calls faster.
    """
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json"
    })
    yield session
    session.close()


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture
def valid_user_payload():
    """
    Standard valid user payload for POST tests.
    Fixture so every test gets a fresh dict — no shared state.
    """
    return {
        "name": "Divya Kumar",
        "job": "Senior SDET"
    }


@pytest.fixture
def updated_user_payload():
    """Standard payload for PUT/PATCH tests."""
    return {
        "name": "Divya Kumar",
        "job": "Lead SDET"
    }