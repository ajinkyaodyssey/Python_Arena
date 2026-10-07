# week5/day23/conftest.py
# day23-specific fixtures only.
# api_client and base_url come from week5/conftest.py automatically.

import pytest


@pytest.fixture
def valid_user_payload():
    """Fresh valid user payload for POST tests."""
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
