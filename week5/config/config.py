# week5/config/config.py
# Central configuration for the API test suite.
# All environment variables read from one place.
#
# WHY THIS EXISTS:
# If os.getenv("REQRES_API_KEY") is scattered across 20 test files,
# changing the variable name means finding and updating 20 files.
# Centralising here means: change once, everything else still works.
#
# HOW IT WORKS:
# python-dotenv reads .env file and loads variables into os.environ.
# os.getenv() then reads from os.environ.
# If .env is missing (e.g. in CI), variables must be set another way
# (GitHub Actions secrets, shell export, etc.)

import os
from pathlib import Path
from dotenv import load_dotenv

# Find project root (where .env lives)
# This works regardless of which directory pytest is run from
PROJECT_ROOT = Path(__file__).parent.parent.parent      # __file__ = current file → parent = 1 level up → parent = 2 → parent = 3 (project root)
ENV_FILE = PROJECT_ROOT / ".env"

# Load .env file — silently ignored if file does not exist
# In CI, variables are set via GitHub Actions secrets instead
load_dotenv(ENV_FILE)


def _require(key: str) -> str:
    """
    Get a required environment variable.
    Raises clear error if missing — better than cryptic KeyError later.
    """
    value = os.getenv(key)      # Get the value of environment variable 'key'; returns None if missing
    if not value:
        raise EnvironmentError(
            f"Required environment variable '{key}' is not set.\n"
            f"Add it to your .env file: {ENV_FILE}\n"
            f"See .env.example for the list of required variables."
        )
    return value
    

def _optional(key: str, default: str = "") -> str:
    """Get an optional environment variable with a default."""
    return os.getenv(key, default)      # os.getenv(key, default = None) -> Try to get a value from an environment variable. If it doesn't exist, use the default value  


# =============================================
# API CONFIGURATION
# =============================================

class APIConfig:
    """Configuration for the reqres.in API test suite."""

    # Required — tests skip if not set
    API_KEY: str = _require("REQRES_API_KEY")

    # Optional with sensible defaults
    BASE_URL: str = _optional(
        "REQRES_BASE_URL",
        "https://reqres.in/api"
    )

    # Known test credentials (not real secrets but centralised)
    VALID_EMAIL: str = _optional(
        "REQRES_VALID_EMAIL",
        "eve.holt@reqres.in"
    )
    VALID_PASSWORD: str = _optional(
        "REQRES_VALID_PASSWORD",
        "cityslicka"
    )


# =============================================
# PLAYWRIGHT CONFIGURATION
# =============================================

class PlaywrightConfig:
    """Configuration for the Playwright test suite."""

    BASE_URL: str = _optional(
        "SAUCE_BASE_URL",
        "https://www.saucedemo.com"
    )
    USERNAME: str = _optional(
        "SAUCE_USERNAME",
        "standard_user"
    )
    PASSWORD: str = _optional(
        "SAUCE_PASSWORD",
        "secret_sauce"
    )


# =============================================
# REPORTING CONFIGURATION
# =============================================

class ReportConfig:
    """Configuration for test reporting."""

    REPORT_DIR: str = _optional("REPORT_DIR", "reports")
    SCREENSHOT_DIR: str = _optional(
        "SCREENSHOT_DIR",
        "reports/screenshots"
    )


# =============================================
# ENVIRONMENT INFORMATION
# =============================================

class EnvConfig:
    """Which environment tests are running against."""

    ENV: str = _optional("TEST_ENV", "staging")

    @property   # @property is a Python decorator that lets you use a method like an attribute (without calling it with ())
    def is_staging(self) -> bool:
        return self.ENV == "staging"

    @property
    def is_production(self) -> bool:
        return self.ENV == "production"


# Singleton instances — import these directly
api_config = APIConfig()
playwright_config = PlaywrightConfig()
report_config = ReportConfig()
env_config = EnvConfig()
