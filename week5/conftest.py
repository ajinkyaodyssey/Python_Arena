# week5/conftest.py
# Shared fixtures for ALL week5 API tests.
# Uses central config module — no os.getenv() calls here.

import time
import pytest
import requests
import logging
from week5.config.config import api_config

log = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def base_url() -> str:
    """Base URL from config. Single point of change."""
    return api_config.BASE_URL


@pytest.fixture(scope="session")
def api_client():
    """
    Session-scoped authenticated HTTP client.

    x-api-key loaded from config (which reads from .env).
    Never hardcoded — never in git history.

    If API key is not set, tests skip with a clear message
    telling you exactly what to do to fix it.
    """
    if not api_config.API_KEY:
        pytest.skip(
            "REQRES_API_KEY not configured. "
            "Add it to .env file. See .env.example."
        )

    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json",
        "x-api-key": api_config.API_KEY
    })

    log.info(
        f"API client ready. "
        f"Base URL: {api_config.BASE_URL}. "
        f"Key: {api_config.API_KEY[:4]}****"
    )

    yield session
    session.close()
    log.info("API client session closed")


@pytest.fixture(scope="session")
def valid_credentials() -> dict:
    return {
        "email": api_config.VALID_EMAIL,
        "password": api_config.VALID_PASSWORD
    }


@pytest.fixture(scope="session")
def invalid_credentials() -> dict:
    return {
        "email": "invalid@notregistered.com",
        "password": "wrongpassword"
    }

@pytest.fixture(autouse=True)
def rate_limit_guard():
    """Small delay between API calls to avoid rate limiting in CI."""
    yield
    time.sleep(0.5)