# week7/day36/test_container_env.py
# Tests that verify the container environment is correct.
# These run inside Docker to confirm setup is right.
# Run with: docker run --rm python-arena pytest week7/day36/ -v

import sys
import os
import pytest
import importlib


def test_python_version_is_312():
    """
    Container must run Python 3.12 exactly.
    Version mismatch between local and CI = subtle bugs.
    match_fields syntax: major, minor only (not patch)
    """
    version = sys.version_info
    assert version.major == 3, f"Expected Python 3, got {version.major}"
    assert version.minor == 12, (
        f"Expected Python 3.12, got 3.{version.minor}. "
        f"Update Dockerfile FROM line."
    )
    print(f"\n  Python version: {sys.version}")


def test_required_packages_are_installed():
    """
    All packages from requirements.txt must be importable.
    A missing package in the container = silent CI failure.
    """
    required = [
        "pytest",
        "playwright",
        "requests",
        "jsonschema",
        "dotenv",
        "flake8",
    ]
    missing = []
    for package in required:
        try:
            importlib.import_module(package)
        except ImportError:
            missing.append(package)

    assert not missing, (
        f"Required packages not installed in container: {missing}\n"
        f"Check requirements.txt and rebuild the image."
    )
    print(f"\n  All {len(required)} required packages installed")


def test_playwright_chromium_is_installed():
    """
    Chromium browser must be installed and launchable.
    playwright install --with-deps must have run during build.
    """
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        version = browser.version
        browser.close()

    assert version, "Chromium launched but returned no version"
    print(f"\n  Chromium version: {version}")


def test_working_directory_is_app():
    """
    Container working directory must be /app.
    Relative paths in pytest commands depend on this.
    """
    cwd = os.getcwd()
    assert cwd == "/app", (
        f"Expected working directory /app, got {cwd}. "
        f"Check WORKDIR in Dockerfile."
    )
    print(f"\n  Working directory: {cwd}")


def test_pythonunbuffered_is_set():
    """
    PYTHONUNBUFFERED must be set.
    Without it, print() output is buffered and
    disappears from CI logs when tests run fast.
    """
    value = os.environ.get("PYTHONUNBUFFERED")
    assert value == "1", (
        f"PYTHONUNBUFFERED not set to 1, got: {value}. "
        f"Add ENV PYTHONUNBUFFERED=1 to Dockerfile."
    )
    print(f"\n  PYTHONUNBUFFERED={value}")


def test_secrets_are_not_baked_into_image():
    """
    .env file must NOT exist inside the container.
    If it does, secrets were copied into the image — a
    critical security vulnerability. Anyone who pulls
    the image can read your API keys.
    """
    env_path = "/app/.env"
    assert not os.path.exists(env_path), (
        f".env file found at {env_path} inside container. "
        f"Add .env to .dockerignore immediately. "
        f"Rebuild the image. Rotate any secrets that were exposed."
    )
    print(f"\n  .env not present in container — secure")