# week5/day24/conftest.py
# day24-specific fixtures only.
# api_client and base_url come from week5/conftest.py automatically.

# No additional fixtures needed for day24.




# ----------------------------------------------------

# # week5/day24/conftest.py
# import pytest
# import requests

# BASE_URL = "https://reqres.in/api"


# @pytest.fixture(scope="session")
# def api_client():
#     session = requests.Session()
#     session.headers.update({
#         "Content-Type": "application/json",
#         "Accept": "application/json"
#     })
#     yield session
#     session.close()


# @pytest.fixture(scope="session")
# def base_url():
#     return BASE_URL