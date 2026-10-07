# week5/day24/schemas.py
# Central schema library for reqres.in API responses.
# All schemas defined once here, imported wherever needed.
#
# DESIGN PRINCIPLE:
# Schemas should be as specific as possible without being brittle.
# Too loose: {"type": "object"} — catches nothing
# Too strict: {"enum": ["janet.weaver@reqres.in"]} — breaks on data change
# Right: {"type": "string", "minLength": 1} — validates structure not values


# =============================================
# REUSABLE FIELD DEFINITIONS
# =============================================
# Build complex schemas from simple reusable pieces.
# Same way you build functions from smaller functions.

# A non-empty string — most common field type
NON_EMPTY_STRING = {
    "type": "string",
    "minLength": 1
}

# A positive integer — for IDs
POSITIVE_INTEGER = {
    "type": "integer",
    "minimum": 1
}

# A URL string — for avatar, support URL
URL_STRING = {
    "type": "string",
    "minLength": 10,
    "pattern": r"^https?://"
}

# ISO 8601 timestamp — for createdAt, updatedAt
TIMESTAMP_STRING = {
    "type": "string",
    "minLength": 1,
    "pattern": r"^\d{4}-\d{2}-\d{2}T"
}

# Email format — basic validation
EMAIL_STRING = {
    "type": "string",
    "minLength": 5,
    "pattern": r"^[^@]+@[^@]+\.[^@]+"
}


# =============================================
# USER OBJECT SCHEMA
# =============================================
# Used in: GET /api/users/{id} and GET /api/users (list)
# Validates a single user object inside "data"

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
    # ,
    # "additionalProperties": False
    # additionalProperties: False means ANY field not listed above
    # causes a ValidationError. Use this when you want strict contract.
    # Remove it when you want to allow the API to add new fields freely.
}


# =============================================
# SUPPORT OBJECT SCHEMA
# =============================================
# reqres.in includes a "support" object in most responses

SUPPORT_OBJECT_SCHEMA = {
    "type": "object",
    "required": ["url", "text"],
    "properties": {
        "url": URL_STRING,
        "text": NON_EMPTY_STRING
    }
    # ,
    # "additionalProperties": False
}


# =============================================
# SINGLE USER RESPONSE SCHEMA
# =============================================
# Validates: GET /api/users/{id}
# Full response envelope including data + support

SINGLE_USER_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["data", "support"],
    "properties": {
        "data": USER_OBJECT_SCHEMA,
        "support": SUPPORT_OBJECT_SCHEMA
    }
    # ,
    # "additionalProperties": False
}


# =============================================
# LIST USERS RESPONSE SCHEMA
# =============================================
# Validates: GET /api/users?page=N
# Includes pagination metadata + array of users

LIST_USERS_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["page", "per_page", "total", "total_pages", "data", "support"],
    "properties": {
        "page": {
            "type": "integer",
            "minimum": 1
        },
        "per_page": {
            "type": "integer",
            "minimum": 1
        },
        "total": {
            "type": "integer",
            "minimum": 0
        },
        "total_pages": {
            "type": "integer",
            "minimum": 1
        },
        "data": {
            "type": "array",
            "minItems": 0,
            "items": USER_OBJECT_SCHEMA    # each item must match USER_OBJECT_SCHEMA
        },
        "support": SUPPORT_OBJECT_SCHEMA
    }
    # ,
    # "additionalProperties": False
}


# =============================================
# CREATE USER RESPONSE SCHEMA
# =============================================
# Validates: POST /api/users
# Server adds id and createdAt to what you sent

CREATE_USER_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["name", "job", "id", "createdAt"],
    "properties": {
        "name": NON_EMPTY_STRING,
        "job": NON_EMPTY_STRING,
        "id": NON_EMPTY_STRING,    # reqres.in returns id as string for POST
        "createdAt": TIMESTAMP_STRING
    }
    # ,
    # "additionalProperties": False
}


# =============================================
# UPDATE USER RESPONSE SCHEMA
# =============================================
# Validates: PUT /api/users/{id} and PATCH /api/users/{id}
# Server adds updatedAt to what you sent

UPDATE_USER_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["name", "job", "updatedAt"],
    "properties": {
        "name": NON_EMPTY_STRING,
        "job": NON_EMPTY_STRING,
        "updatedAt": TIMESTAMP_STRING
    }
    # ,
    # "additionalProperties": False
}


# =============================================
# LOGIN RESPONSE SCHEMA
# =============================================
# Validates: POST /api/login (successful)

LOGIN_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["token"],
    "properties": {
        "token": NON_EMPTY_STRING
    }
    # ,
    # "additionalProperties": False
}


# =============================================
# ERROR RESPONSE SCHEMA
# =============================================
# Validates: POST /api/login (failed), other error responses

ERROR_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["error"],
    "properties": {
        "error": NON_EMPTY_STRING
    }
    # ,
    # "additionalProperties": False
}


# =============================================
# SCHEMA VALIDATION HELPER
# =============================================
# Wrapper around jsonschema.validate with better error messages.
# Import this instead of using jsonschema directly in tests.

import jsonschema


def validate_schema(response_body: dict, schema: dict, context: str = "") -> None:
    """
    Validate response_body against schema.
    Raises AssertionError with clear message on failure.

    Args:
        response_body: parsed JSON response dict
        schema: jsonschema dict to validate against
        context: optional description for better error messages

    Usage:
        validate_schema(resp.json(), SINGLE_USER_RESPONSE_SCHEMA, "GET /users/2")

    Why use this instead of jsonschema.validate() directly:
        jsonschema raises ValidationError with a long technical message.
        This wrapper converts it to AssertionError with clearer context,
        so pytest shows it as a test failure not an unexpected exception.
    """
    try:
        jsonschema.validate(instance=response_body, schema=schema)
    except jsonschema.ValidationError as e:
        # Build a clear failure message
        path = " -> ".join(str(p) for p in e.absolute_path) or "root"
        raise AssertionError(
            f"Schema validation failed{' for ' + context if context else ''}.\n"
            f"  Path:     {path}\n"
            f"  Problem:  {e.message}\n"
            f"  Got:      {e.instance}\n"
            f"  Schema:   {e.schema}"
        ) from e
    except jsonschema.SchemaError as e:
        raise AssertionError(
            f"Schema itself is invalid: {e.message}"
        ) from e
