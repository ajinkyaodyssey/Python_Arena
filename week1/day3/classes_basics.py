# DAY 3 - FILE 1: Classes and Objects
# Run with: python3 classes_basics.py

# =============================================
# SECTION 1: What a class actually is
# =============================================
# A class is a blueprint. An object is a thing built from that blueprint.
# Every time you call ClassName(), Python runs __init__ and gives you
# a fresh object with its own copy of all instance attributes.

print("=== CLASS BASICS ===")

class TestUser:
    # __init__ runs automatically when you do TestUser(...)
    # self refers to the specific object being created
    # without self, Python does not know WHICH object's data to set
    def __init__(self, username, email, role = "tester"):
        self.username = username    # instance attribute - unique per object
        self.email = email          # instance attribute - unique per object
        self.role = role            # instance attribute - unique per object
        self.login_count = 0        # instance attribute - starts at 0 for everyone
        self.is_active = True       # instance attribute - default True
        
    def login(self):
        self.login_count += 1
        return f"{self.username} logged in (session # {self.login_count})"
            
    def deactivate(self):
        self.is_active = False
        return f"{self.username} has be deactivated"
            
    def get_profile(self):
        return {
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "login count": self.login_count
        }
    
# Creating objects - each is completely independent
user1 = TestUser("divya", "divya@test.com", "sdet")
user2 = TestUser("arjun", "arjun@test.com", "admin")
user3 = TestUser("priya", "priya@test.com")  # uses default role="tester"

# Each object has its OWN login_count
print(user1.login())    # divya logged in (session #1)
print(user1.login())    # divya logged in (session #2)
print(user2.login())    # arjun logged in (session #1)  <-- independent of user1

print(f"\nuser1 login_count: {user1.login_count}")  # 2
print(f"user2 login_count: {user2.login_count}")  # 1
print(f"user3 login_count: {user3.login_count}")  # 0

# Accessing attributes directly
print(f"\nuser1.username: {user1.username}")
print(f"user1.role: {user1.role}")
print(f"user3.role: {user3.role}")  # "tester" - the default

#Addressing attributes directly
print(f"\nReturning profile: {user1.get_profile()}")


# =============================================
# SECTION 2: Modifying attributes
# =============================================


print("\n=== MODIFYING ATTRIBUTES ===")

# You can set attributes directly from outside the class
# You can set attributes directly from outside the class
user1.role = "senior_sdet"          # update
user1.team = "platform"             # add a new attribute (Python allows this)
print(f"Updated role: {user1.role}")
print(f"New attribute team: {user1.team}")

# Calling a method that modifies state
result = user2.deactivate()
print(result)
print(f"user2.is_active: {user2.is_active}")   # False
print(f"user1.is_active: {user1.is_active}")   # True - not affected


# =============================================
# SECTION 3: __str__ and __repr__
# =============================================


print("\n=== __STR__ AND __REPR__ ===")

# Without __str__ and __repr__, printing an object looks like:
# <__main__.TestUser object at 0x7f1234567890>
# That is useless. These two methods fix that.

class BetterTestUser:
    def __init__(self, username, email, role = "tester"):
        self.username = username
        self.email = email
        self.role = role
        self.login_count = 0
        
    def __str__(self):
        #Called by print() and str()
        #should be READABLE for humans
        return f"TestUser ({self.username} | {self.role})"
        
    def __repr__(self):
        #Called by the debugger, logs when object is inside the list
        #Should be UNAMBIGIOUS - ideally recreateable
        #the !r tells Python to use repr() on the value instead of str()
        return f"BetterTestUser(username: {self.username!r}, email: {self.email!r}, role: {self.role!r})"
        
    def login(self):
        self.login_count+=1
        return f"{self.username} logged in"
        
u = BetterTestUser("divya", "divya@test.com", "sdet")
v = BetterTestUser("arjun", "arjun@test.com", "admin")

print(str(u))           # TestUser(divya | sdet)    -- calls __str__
print(u)                # TestUser(divya | sdet)    -- print() also calls __str__
print(repr(u))          # BetterTestUser(username='divya', ...)  -- calls __repr__

# When inside a list, __repr__ is called not __str__
users_list = [u, v]
print(users_list)       # shows __repr__ for each object

#the !r in f-strings calls repr() on the value
name = "divya"
print(f"Name is: {name!r}")   # Name is: 'divya'  -- includes quotes
print(f"Name is: {name}")     # Name is: divya    -- no quotes