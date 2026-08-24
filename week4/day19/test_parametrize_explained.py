# week4/day19/test_parametrize_explained.py
# Understand parametrize before using it in real tests
# Run with: pytest week4/day19/test_parametrize_explained.py -v

import pytest


# =============================================
# BEFORE PARAMETRIZE — the problem
# =============================================
# These 3 tests are identical except for the input.
# If the logic changes, you update 3 places.
# If you add a new case, you add a whole new function.
# This is the copy-paste problem parametrize solves.

def test_empty_string_is_falsy_manual():
    assert not bool("")

def test_zero_is_falsy_manual():
    assert not bool(0)

def test_none_is_falsy_manual():
    assert not bool(None)


# =============================================
# AFTER PARAMETRIZE — the solution
# =============================================
# One test function. Three data rows.
# pytest runs it three times, once per row.
# Adding a new case = adding one line to the list.

@pytest.mark.parametrize("value", ["", 0, None, [], {}])
def test_falsy_values(value):
    assert not bool(value)

# pytest generates test IDs automatically:
# test_falsy_values[-]     <- "" (empty string)
# test_falsy_values[0]     <- 0
# test_falsy_values[value3] <- None
# test_falsy_values[value4] <- []
# test_falsy_values[value5] <- {}


# =============================================
# MULTIPLE PARAMETERS
# =============================================
# Pass multiple values per test case as a tuple.
# The function receives them as separate arguments.

@pytest.mark.parametrize("input_val, expected", [
    (2 + 2, 4),
    (10 - 3, 7),
    (3 * 3, 9),
    (10 / 2, 5.0),
])
def test_math_operations(input_val, expected):
    assert input_val == expected


# =============================================
# CUSTOM IDS — make test names readable
# =============================================
# Default IDs are auto-generated and often unreadable.
# pytest.param(..., id="name") gives you a human-readable name.

@pytest.mark.parametrize("status_code, expected_category", [
    pytest.param(200, "success", id="OK"),          # pytest.param(input, expected, id="name")
    pytest.param(201, "success", id="Created"),
    pytest.param(404, "client_error", id="Not_Found"),
    pytest.param(500, "server_error", id="Internal_Server_Error"),
])
def test_status_code_category(status_code, expected_category):
    if 200 <= status_code < 300:
        category = "success"
    elif 400 <= status_code < 500:
        category = "client_error"
    else:
        category = "server_error"
    assert category == expected_category

# Test names become:
# test_status_code_category[OK]
# test_status_code_category[Created]
# test_status_code_category[Not_Found]
# test_status_code_category[Internal_Server_Error]
# Much clearer in CI output than test_status_code_category[200-success]

# (200, "success") → simple test data
# pytest.param(200, "success", id="OK") → test data + extra pytest information


# =============================================
# MARKS ON INDIVIDUAL PARAMETRIZE CASES
# =============================================
# You can apply different marks to individual test cases.
# pytest.param() allows you to give each case its own ID
# and apply marks such as skip, xfail, or slow.

@pytest.mark.parametrize("n, expected", [
    # n = input value, expected = expected Fibonacci result
    pytest.param(1, 1, id="base_case_1"),
    pytest.param(2, 1, id="base_case_2"),
    pytest.param(5, 5, id="fifth_fibonacci"),
    pytest.param(10, 55, id="tenth_fibonacci"),
    
    # This specific test case is marked as slow
    pytest.param(
        50, 12586269025,
        id="large_number",
        marks=pytest.mark.slow
    ),
])
def test_fibonacci(n, expected):
    # Define a Fibonacci function inside the test
    def fib(n):
        # Start with the first two Fibonacci values
        a, b = 0, 1
        
        # Repeat n times to calculate the Fibonacci number
        for _ in range(n):
            a, b = b, a + b
        
        # Return the calculated Fibonacci value
        return a
    
    # Compare the actual result with the expected result
    assert fib(n) == expected


# =============================================
# PARAMETRIZE + FIXTURES
# =============================================
# Parametrize and fixtures work together.
# The fixture runs fresh for each parametrized case.

@pytest.fixture
def multiplier():
    return 10

@pytest.mark.parametrize("value, expected", [
    (1, 10),
    (5, 50),
    (0, 0),
])
def test_multiply_with_fixture(value, expected, multiplier):
    # fixture 'multiplier' runs once per parameterized case 
    assert value * multiplier == expected