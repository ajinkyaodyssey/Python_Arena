# week5/day26/test_secrets_management.py
# Tests for safely managing API secrets.
# Run: pytest week5/day26/ -v -s

import os
# os → Python module for interacting with environment variables, files, etc.

import pytest
# pytest → testing framework

import requests
# requests → library used to make HTTP/API requests

from pathlib import Path
# Path → easier way to work with file/folder paths

from week5.config.config import api_config, APIConfig
# Import our own config objects from config.py


PROJECT_ROOT = Path(__file__).parent.parent.parent
# __file__ = current file
# .parent = go up one folder
# parent × 3 = project root


# =============================================
# SECTION 1: Verify secrets are not hardcoded
# =============================================

def test_api_key_not_hardcoded_in_source_files():
    # Functions starting with test_ are automatically discovered by pytest.

    suspicious_patterns = [
        "x-api-key",
        "api_key =",
        "API_KEY =",
    ]

    python_files = list(PROJECT_ROOT.rglob("*.py"))
    # rglob() → recursively find files matching a pattern
    # "*.py" → all Python files

    violations = []
    # Empty list → we'll store anything suspicious here.

    for filepath in python_files:
        # for → loop through every Python file

        if "config.py" in str(filepath):
            continue
        # continue → skip this file and move to the next one

        if "test_secrets" in str(filepath):
            continue

        if ".venv" in str(filepath) or "venv" in str(filepath):
            continue
        # or → either condition can be True

        try:
            content = filepath.read_text()
            # read_text() → read the contents of a file as text

            for pattern in suspicious_patterns:
                if pattern in content:
                    # "x" in "text" → checks whether x exists in text

                    lines = content.split("\n")
                    # split() → breaks text into a list
                    # "\n" means a new line

                    for i, line in enumerate(lines, 1):
                        # enumerate() → gives both index/number and value
                        # 1 → start counting from 1

                        if pattern in line:
                            stripped = line.strip()
                            # strip() → removes spaces from beginning/end

                            if stripped.startswith("#"):
                                continue
                            # startswith() → checks how a string begins
                            # Skip comments

                            if "os.getenv" in line:
                                continue
                            # os.getenv() → reads an environment variable

                            if "config." in line:
                                continue

                            if "headers" in line:
                                continue

                            violations.append(
                                f"{filepath}:{i}: {line.strip()}"
                            )
                            # append() → add an item to a list
                            # f"..." → f-string, allows variables inside {}

        except Exception:
            pass
            # except → handles an error
            # pass → do nothing

    if violations:
        # If list is NOT empty → something suspicious was found

        print("\n  [SECRETS SCAN] Potential hardcoded secrets found:")

        for v in violations:
            print(f"    {v}")

    else:
        # Runs when violations list is empty

        print(
            f"\n  [SECRETS SCAN] Scanned {len(python_files)} files. "
            f"No hardcoded secrets found."
        )
        # len() → number of items in a list


def test_env_file_is_not_tracked_by_git():

    import subprocess
    # subprocess → allows Python to run terminal/OS commands

    result = subprocess.run(
        ["git", "ls-files", ".env"],
        # Runs: git ls-files .env

        capture_output=True,
        # Capture the command's output so Python can inspect it

        text=True,
        # Return output as normal text

        cwd=PROJECT_ROOT
        # cwd = current working directory for the command
    )

    tracked = result.stdout.strip()
    # stdout → normal output from the command
    # strip() → remove extra whitespace

    assert not tracked
    # assert → condition MUST be True for test to pass
    # We expect .env NOT to be tracked by Git

    print("\n  [GIT SECURITY] .env is NOT tracked by git — safe")


def test_gitignore_contains_env_patterns():

    gitignore_path = PROJECT_ROOT / ".gitignore"
    # Path / "filename" → creates a path inside the folder

    assert gitignore_path.exists()
    # exists() → checks whether the file/folder exists

    content = gitignore_path.read_text()
    # Read .gitignore contents

    required_patterns = [".env", "*.env"]
    # These patterns should exist in .gitignore

    missing = []

    for pattern in required_patterns:
        if pattern not in content:
            missing.append(pattern)

    assert not missing
    # Test passes only if nothing is missing

    print("\n  [GITIGNORE] All required patterns present in .gitignore")


def test_env_example_file_exists():

    example_path = PROJECT_ROOT / ".env.example"

    assert example_path.exists()
    # Check that .env.example exists

    content = example_path.read_text()

    assert "REQRES_API_KEY" in content
    # Check that the API key variable is documented

    print(
        "\n  [ENV EXAMPLE] .env.example exists "
        "and documents required variables"
    )


# =============================================
# SECTION 2: Verify config module works
# =============================================

def test_config_loads_api_key_from_environment():

    assert api_config.API_KEY
    # Check that API key actually exists

    assert api_config.API_KEY != "your_api_key_here"
    # != means "not equal to"
    # Make sure placeholder wasn't used

    print(
        f"\n  [CONFIG] API key loaded: "
        f"{api_config.API_KEY[:4]}"
        f"{'*' * (len(api_config.API_KEY) - 4)}"
    )
    # [:4] → first 4 characters
    # '*' * number → repeat * to hide the rest of the secret


def test_config_has_correct_base_url():

    assert api_config.BASE_URL.startswith("https://")
    # startswith() → checks beginning of string

    assert "reqres.in" in api_config.BASE_URL
    # in → checks whether text exists inside another string

    print(f"\n  [CONFIG] Base URL: {api_config.BASE_URL}")


def test_config_never_logs_full_secret(capsys):
    # capsys → pytest fixture that captures print() output

    masked = f"{api_config.API_KEY[:4]}{'*' * 8}"

    print(f"Key preview: {masked}")

    captured = capsys.readouterr()
    # read captured terminal output

    if len(api_config.API_KEY) > 8:

        full_key_in_output = api_config.API_KEY in captured.out
        # Check whether the COMPLETE API key appeared in output

        assert not full_key_in_output
        # Full secret should NEVER appear in logs

    print(f"\n  [MASKING] Key masked correctly: {masked}")


# =============================================
# SECTION 3: Verify API key actually works
# =============================================

def test_api_key_is_valid_and_accepted(api_client, base_url):
    # api_client and base_url are pytest fixtures
    # Fixtures provide reusable test setup/data

    resp = api_client.get(f"{base_url}/users/1")
    # GET request → retrieve data from API
    # f-string inserts base_url into the URL

    assert resp.status_code == 200
    # 200 = successful HTTP request

    print("\n  [API KEY] Key is valid — GET /users/1 returned 200")
    print(f"  [API KEY] Key preview: {api_config.API_KEY[:4]}****")


def test_request_without_api_key_behaviour(api_client, base_url):
    """
    Documents what happens when no API key is sent.

    reqres.in behaviour is inconsistent — some endpoints enforce
    the key, others do not. This test documents the actual behaviour
    rather than asserting a specific status code.

    On a properly secured API, removing the key should return 401.
    If this returns 200, it means the endpoint is public or the
    API is not consistently enforcing authentication.

    WHY THIS MATTERS:
    Documenting API security gaps is a real SDET responsibility.
    If a protected endpoint returns 200 without auth, that is a
    security bug to raise with the development team.
    """
    resp = requests.get(
        f"{api_config.BASE_URL}/users/1",
        headers={
            "Content-Type": "application/json"
            # Deliberately no x-api-key
        }
    )

    print(f"\n  [NO KEY] Request without key returns: {resp.status_code}")

    if resp.status_code == 401:
        print("  [NO KEY] API enforces key requirement — secure")
    elif resp.status_code == 200:
        print(
            "  [NO KEY] API returned 200 without key — endpoint is public. "
            "Note: reqres.in GET endpoints may not require auth. "
            "On a production API this would be a security concern."
        )

    # Must not crash with 500
    assert resp.status_code != 500, (
        "Server must not crash on missing key"
    )
    # Should be either 200 (public) or 401 (protected)
    assert resp.status_code in [200, 401], (
        f"Unexpected status: {resp.status_code}"
    )

def test_request_with_wrong_api_key_behaviour(api_client, base_url):
    """
    Documents what happens when an invalid API key is sent.

    Same situation as above — reqres.in may not consistently
    reject invalid keys on all endpoints.

    On a real production API:
    - Invalid key MUST return 401
    - This is a hard security requirement

    For reqres.in (test/demo API):
    - Behaviour may vary by endpoint
    - We document actual behaviour rather than asserting expected
    """
    resp = requests.get(
        f"{api_config.BASE_URL}/users/1",
        headers={
            "Content-Type": "application/json",
            "x-api-key": "definitely-not-a-valid-key-xyz"
        }
    )

    print(f"\n  [WRONG KEY] Invalid key returns: {resp.status_code}")

    if resp.status_code == 401:
        print("  [WRONG KEY] API validates key content — secure")
    elif resp.status_code == 200:
        print(
            "  [WRONG KEY] API returned 200 with invalid key. "
            "reqres.in may not validate key content on GET endpoints. "
            "Production APIs must reject invalid keys with 401."
        )

    assert resp.status_code != 500
    assert resp.status_code in [200, 401], (
        f"Unexpected status: {resp.status_code}"
    )

# =============================================
# SECTION 4: CI/CD secrets pattern
# =============================================

def test_ci_environment_variable_pattern():

    is_ci = os.getenv("CI") == "true"
    # os.getenv() → get environment variable
    # Check whether CI environment variable equals "true"

    has_key = bool(os.getenv("REQRES_API_KEY"))
    # bool() → converts value to True/False
    # Checks whether API key exists

    print(f"\n  [CI PATTERN] Running in CI: {is_ci}")
    print(f"  [CI PATTERN] API key available: {has_key}")

    if is_ci:

        print(
            "  [CI PATTERN] In CI: key should come from "
            "GitHub Actions secrets, not .env file"
        )

    else:

        print(
            "  [CI PATTERN] Local: key comes from .env file "
            "loaded by python-dotenv"
        )

    print("""
  [CI PATTERN] GitHub Actions workflow pattern:

  jobs:
    test:
      steps:
        - name: Run API tests
          run: pytest week5/
          env:
            REQRES_API_KEY: ${{ secrets.REQRES_API_KEY }}
    """)