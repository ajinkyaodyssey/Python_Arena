# week5/saturday_project/tests/api/schemas.py
# Central schema library for the reqres.in API test suite.
# All schemas in one file — change API contract, update one place.

import jsonschema

# =============================================
# REUSABLE FIELD DEFINITIONS
# =============================================

NON_EMPTY_STRING = {"type": "string", "minLength": 1}
POSITIVE_INTEGER = {"type": "integer", "minimum": 1}
URL_STRING = {
    "type": "string",
    "minLength": 10,
    "pattern": r"^https?://"
}
TIMESTAMP_STRING = {
    "type": "string",
    "minLength": 1
}
EMAIL_STRING = {
    "type": "string",
    "minLength": 5,
    "pattern": r"^[^@]+@[^@]+\.[^@]+"
}

# =============================================
# OBJECT SCHEMAS
# =============================================

USER_OBJECT_SCHEMA = {
    "type": "object",
    "required": ["id", "email", "first_name", "last_name", "avatar"],
    "properties": {
        "id": POSITIVE_INTEGER,
        "email": EMAIL_STRING,
        "first_name": NON_EMPTY_STRING,
        "last_name": NON_EMPTY_STRING,
        "avatar": URL_STRING
    }
}

SUPPORT_OBJECT_SCHEMA = {
    "type": "object",
    "required": ["url", "text"],
    "properties": {
        "url": URL_STRING,
        "text": NON_EMPTY_STRING
    }
}

SINGLE_USER_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["data", "support"],
    "properties": {
        "data": USER_OBJECT_SCHEMA,
        "support": SUPPORT_OBJECT_SCHEMA
    }
}

LIST_USERS_RESPONSE_SCHEMA = {
    "type": "object",
    "required": [
        "page", "per_page", "total",
        "total_pages", "data", "support"
    ],
    "properties": {
        "page": {"type": "integer", "minimum": 1},
        "per_page": {"type": "integer", "minimum": 1},
        "total": {"type": "integer", "minimum": 0},
        "total_pages": {"type": "integer", "minimum": 1},
        "data": {
            "type": "array",
            "items": USER_OBJECT_SCHEMA
        },
        "support": SUPPORT_OBJECT_SCHEMA
    }
}

CREATE_USER_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["name", "job", "id", "createdAt"],
    "properties": {
        "name": NON_EMPTY_STRING,
        "job": NON_EMPTY_STRING,
        "id": NON_EMPTY_STRING,
        "createdAt": TIMESTAMP_STRING
    }
}

UPDATE_USER_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["name", "job", "updatedAt"],
    "properties": {
        "name": NON_EMPTY_STRING,
        "job": NON_EMPTY_STRING,
        "updatedAt": TIMESTAMP_STRING
    }
}

LOGIN_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["token"],
    "properties": {
        "token": NON_EMPTY_STRING
    }
}

REGISTER_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["id", "token"],
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "token": NON_EMPTY_STRING
    }
}

ERROR_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["error"],
    "properties": {
        "error": NON_EMPTY_STRING
    }
}


# =============================================
# VALIDATION HELPER
# =============================================

def validate(body: dict, schema: dict, context: str = "") -> None:
    """
    Validate response body against schema.
    Raises AssertionError with clear message on failure.
    """
    try:
        jsonschema.validate(instance=body, schema=schema)
    except jsonschema.ValidationError as e:
        path = " -> ".join(str(p) for p in e.absolute_path) or "root"
        raise AssertionError(
            f"Schema validation failed"
            f"{' for ' + context if context else ''}.\n"
            f"  Path:    {path}\n"
            f"  Problem: {e.message}\n"
            f"  Got:     {e.instance}"
        ) from e