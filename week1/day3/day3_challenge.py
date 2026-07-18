# DAY 3 - FILE 4: Challenge
# Build TestUser entirely from scratch
# Run with: python3 day3_challenge.py

# INSTRUCTIONS:
# Build a TestUser class with ALL of the following:
#
# Attributes set in __init__:
#   - username (str)
#   - email (str)
#   - role (str, default="tester")
#   - is_active (bool, default=True)
#   - login_count (int, default=0)
#   - _permissions (list, default=[])   <- note the underscore
#
# Class attribute:
#   - default_role = "tester"
#   - _total_users = 0  (increments each time a user is created)
#
# Instance methods (5):
#   1. login()
#      - increments login_count by 1
#      - returns f"{username} logged in (session #{login_count})"
#      - raises PermissionError if is_active is False
#
#   2. deactivate()
#      - sets is_active to False
#      - returns f"{username} has been deactivated"
#
#   3. add_permission(permission)
#      - adds permission string to _permissions if not already there
#      - returns True if added, False if already existed
#
#   4. has_permission(permission)
#      - returns True if permission is in _permissions, False otherwise
#
#   5. get_profile()
#      - returns a dict with all public attributes
#      - keys: "username", "email", "role", "is_active",
#              "login_count", "permissions"
#
# Class method:
#   - from_dict(cls, data) - creates TestUser from a dict
#     data has keys: "username", "email", and optionally "role"
#
# Static method:
#   - is_valid_email(email) - returns True if "@" in email
#     and "." in the part after "@"
#
# Dunder methods:
#   - __str__  returns "TestUser(username | role | active/inactive)"
#   - __repr__ returns "TestUser(username='x', email='y', role='z')"
#   - __eq__   two TestUsers are equal if their usernames match


class TestUser:
    default_role = "tester"
    _total_users = 0
    
    def __init__(self, username, email, role = "tester", is_active = True, login_count = 0, _permissions = None):
    
        self.username = username
        self.email = email
        self.role = role
        self.is_active = is_active
        self.login_count = login_count
        self._permissions = _permissions or []
        TestUser._total_users +=1
    
    def login(self):
        if self.is_active == True:
            self.login_count+=1
            return f"{self.username} logged in (session #{self.login_count})"
        else:
            raise PermissionError
        
    def deactivate(self):
        self.is_active = False
        return f"{self.username} has been deactivated"
        
    def add_permission(self, permissions):
        if permissions in self._permissions:
            return False
        else:
            self._permissions.append(permissions)
            return True
            
    def has_permission(self, permission):
        return permission in self._permissions
            
    def get_profile(self):
        return {
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "login_count": self.login_count,
            "permissions": self._permissions
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            data["username"], 
            data["email"], 
            data.get("role","tester")
            )

    @staticmethod
    def is_valid_email(email):
        return "@" in email and "." in email.split("@")[1] 
        
    def __str__(self):
        return f"TestUser({self.username} | {self.role} | {self.is_active})"
    
    def __repr__(self):
        return f"TestUser(Username = {self.username!r}, email = {self.email!r}, role = {self.role!r})"
        
    def __eq__(self, other):
        if not isinstance(other, TestUser):
            return NotImplemented
        return self.username == other.username
    
    


# =============================================
# DO NOT MODIFY BELOW THIS LINE
# =============================================

print("=== TESTING TestUser ===\n")

# Test 1: Basic creation and instance attributes
u1 = TestUser("divya", "divya@test.com", "sdet")
assert u1.username == "divya", "1a"
assert u1.email == "divya@test.com", "1b"
assert u1.role == "sdet", "1c"
assert u1.is_active == True, "1d"
assert u1.login_count == 0, "1e"
print("TEST 1 PASSED: Basic creation")

# Test 2: Default role
u2 = TestUser("arjun", "arjun@test.com")
assert u2.role == "tester", "2a"
print("TEST 2 PASSED: Default role")

# Test 3: Class attribute
assert TestUser.default_role == "tester", "3a"
print("TEST 3 PASSED: Class attribute")

# Test 4: login()
result = u1.login()
assert u1.login_count == 1, "4a"
assert "divya" in result, "4b"
assert "1" in result, "4c"
u1.login()
assert u1.login_count == 2, "4d"
print("TEST 4 PASSED: login()")

# Test 5: login() raises on inactive user
u2.deactivate()
try:
    u2.login()
    assert False, "5a - should have raised PermissionError"
except PermissionError:
    pass
print("TEST 5 PASSED: login() raises on inactive")

# Test 6: deactivate()
u3 = TestUser("priya", "priya@test.com")
msg = u3.deactivate()
assert u3.is_active == False, "6a"
assert "priya" in msg, "6b"
print("TEST 6 PASSED: deactivate()")

# Test 7: add_permission() and has_permission()
u4 = TestUser("admin", "admin@test.com", "admin")
assert u4.add_permission("read") == True, "7a"
assert u4.add_permission("write") == True, "7b"
assert u4.add_permission("read") == False, "7c"  # already exists
assert u4.has_permission("read") == True, "7d"
assert u4.has_permission("delete") == False, "7e"
print("TEST 7 PASSED: add_permission() and has_permission()")

# Test 8: get_profile()
profile = u4.get_profile()
assert profile["username"] == "admin", "8a"
assert profile["email"] == "admin@test.com", "8b"
assert profile["role"] == "admin", "8c"
assert profile["is_active"] == True, "8d"
assert "read" in profile["permissions"], "8e"
assert "write" in profile["permissions"], "8f"
print("TEST 8 PASSED: get_profile()")

# Test 9: from_dict() class method
data = {"username": "ravi", "email": "ravi@test.com", "role": "lead"}
u5 = TestUser.from_dict(data)
assert u5.username == "ravi", "9a"
assert u5.role == "lead", "9b"

data2 = {"username": "sara", "email": "sara@test.com"}
u6 = TestUser.from_dict(data2)
assert u6.role == "tester", "9c"  # default role
print("TEST 9 PASSED: from_dict()")

# Test 10: is_valid_email() static method
assert TestUser.is_valid_email("divya@test.com") == True, "10a"
assert TestUser.is_valid_email("divya@test") == False, "10b"
assert TestUser.is_valid_email("divyatest.com") == False, "10c"
assert TestUser.is_valid_email("") == False, "10d"
print("TEST 10 PASSED: is_valid_email()")

# Test 11: __str__
s = str(u1)
assert "divya" in s, "11a"
assert "sdet" in s, "11b"
print("TEST 11 PASSED: __str__")

# Test 12: __repr__
r = repr(u1)
assert "divya" in r, "12a"
assert "divya@test.com" in r, "12b"
print("TEST 12 PASSED: __repr__")

# Test 13: __eq__
u7 = TestUser("divya", "other@email.com", "admin")
assert u1 == u7, "13a"       # same username = equal
assert u1 != u2, "13b"       # different username = not equal
print("TEST 13 PASSED: __eq__")

# Test 14: _total_users class attribute
initial = TestUser._total_users
u8 = TestUser("new_user", "new@test.com")
assert TestUser._total_users == initial + 1, "14a"
print("TEST 14 PASSED: _total_users counter")

print("\nALL 14 TESTS PASSED. Day 3 complete.")