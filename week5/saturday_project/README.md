# API Test Suite — Week 5 Saturday Project

Complete API test suite for the reqres.in REST API.
Built as part of the SDET 90-Day Training Plan.

## Coverage

| File | Class | Tests | What it covers |
|---|---|---|---|
| test_users_get.py | TestGetSingleUser | 10 | Single user retrieval, 404, schema |
| test_users_get.py | TestListUsers | 8 | Pagination, schema, data integrity |
| test_users_write.py | TestCreateUser | 8 | POST 201, schema, timestamps |
| test_users_write.py | TestUpdateUser | 8 | PUT/PATCH 200, schema, partial update |
| test_users_write.py | TestDeleteUser | 5 | DELETE 204, empty body, idempotent |
| test_auth.py | TestLogin | 8 | Login success/failure, schema, token |
| test_auth.py | TestRegister | 5 | Register success/failure, schema |
| test_auth.py | TestAuthToken | 3 | Token fixture, auth header, usage |
| test_edge_cases.py | TestDelayedResponse | 2 | Slow response handling |
| test_edge_cases.py | TestPaginationEdgeCases | 2 | Page bounds, per_page param |
| test_edge_cases.py | TestDataIntegrity | 5 | Cross-endpoint consistency |
| test_edge_cases.py | TestContentNegotiation | 2 | Headers, JSON validity |
| **Total** | | **66** | |

## Design Decisions

### Schema validation on every response
Every test that checks response data also validates
the complete response structure against a schema.
Status code 200 with a missing field fails immediately.

### Negative cases named clearly
Test names describe the condition and expected outcome:
`test_login_missing_password_returns_400`
`test_delete_nonexistent_user_does_not_crash`
No ambiguity about what the test is checking.

### Classes group related tests
All GET single user tests in `TestGetSingleUser`.
All login tests in `TestLogin`.
Running `pytest -k TestLogin` gives you just auth tests.

### Session-scoped api fixture
One authenticated session for the entire run.
Connection pooling + no repeated auth overhead.

## How to Run

```bash
# All tests
pytest week5/saturday_project/ -v

# One class
pytest week5/saturday_project/ -k TestLogin -v

# One file
pytest week5/saturday_project/tests/api/test_auth.py -v

# With HTML report
pytest week5/saturday_project/ -v --html=reports/api_suite_report.html
```

## Environment Setup

```bash
# .env file required
REQRES_API_KEY=your_key_here

# Get key at: app.reqres.in/api-keys
```