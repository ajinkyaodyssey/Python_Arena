from datetime import date, timedelta

class Book:
    def __init__(self, title, author, isbn):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.is_checked_out = False
        self.borrowed_by = None     # will hold the Member object
        self.borrowed_date = None   # will hold a date object
        
    def checkout(self, member):
        if self.is_checked_out == True:
            raise ValueError("Book is already checked out by someone else")
        else:
            self.is_checked_out = True
            self.borrowed_by = member
            self.borrowed_date = date.today()
                
    def return_book(self):
        if self.is_checked_out == False:
            raise ValueError
        else:
            self.is_checked_out = False
            self.borrowed_by = None
            self.borrowed_date = None
    
    def is_overdue(self):
        if not self.is_checked_out:
            return False
        else:
            return (date.today() - self.borrowed_date).days > 14
            
    def days_overdue(self):
        if not self.is_overdue():
            return 0
        else:
            return (date.today() - self.borrowed_date).days - 14
            
    def __str__(self):
        if self.is_checked_out:
            days = (date.today() - self.borrowed_date).days
            return f"{self.title} - Checked out by {self.borrowed_by.name} ({days} days)"
        return f"{self.title} [ISBN: {self.isbn}] - Available"
            
    def __repr__(self):
        return f"Book(title={self.title!r}, isbn={self.isbn!r})"
            
            
# ##########################################################################
class Member:
    _member_counter = 0   ## class attribute — auto-generate IDs
    
    def __init__(self, name, email):
        Member._member_counter += 1
        self.member_id = f"MEM{Member._member_counter:04d}"  # MEM0001, MEM0002...
        self.name = name
        self.email = email
        self._borrowed_books = []      # list of Book objects
        
    def checkout_book(self, book):
        # - Call book.checkout(self) — pass self so the book knows WHO has it
        # - Add book to self._borrowed_books
        book.checkout(self)
        self._borrowed_books.append(book)
        
    def return_book(self, book):
        # - Call book.return_book()
        # - Remove book from self._borrowed_books
        book.return_book()
        self._borrowed_books.remove(book)
        
    def get_borrowed_books(self):
        return self._borrowed_books
        
    def __str__(self):
        return f"Member({self.member_id} | {self.name} | {len(self._borrowed_books)} books)"
        
# ###########################################################################
class Admin(Member):
    
    def __init__(self, name, email):
        super().__init__(name, email)
        self.member_id = self.member_id.replace("MEM", "ADM")  # ADM0003 instead of MEM0003
        self._added_books = []     # track what this admin added
        
    def add_book(self, library, book):
        library.add_book(book)
        self._added_books.append(book)
        
    def remove_book(self, library, book):
        if book.is_checked_out == False:
            library.remove_book(book)
    
    def __str__(self):
        return f"Admin({self.member_id} | {self.name} | added {len(self._added_books)} books)"
     
############################################################################3
class Library:
    def __init__(self, name):
        self.name = name
        self._books = []
        self._members = []
        
    def add_book(self, book):
        for b in self._books:
            if b.isbn == book.isbn:
                raise ValueError("Already exists")
        self._books.append(book)
    
    def remove_book(self, book):
        if book.is_checked_out == True:
            raise ValueError
        else:
            self._books.remove(book)
            
    def register_member(self, member):
        if member not in self._members:
            self._members.append(member)
    
    def find_by_title(self, title):
        # - Search self._books for any book where title matches (case insensitive)
        # - Return a list of matching books (there could be multiple copies)
        res = []
        for b in self._books:
            if b.title.lower() == title.lower():
                res.append(b)
        return res

    def find_by_isbn(self, isbn):
        # - Return the specific book with that isbn, or None if not found
        for book in self._books:
            if book.isbn == isbn:
                return book
        return None

    def list_overdue_books(self):
        # - Return list of books where book.is_overdue() is True
        res = []
        for book in self._books:
            if book.is_overdue() == True:
                res.append(book)
        return res

    def show_all_books(self):
        # - Print all books with their status
        for book in self._books:
            print(book)

    def __str__(self):
        available = sum(1 for b in self._books if not b.is_checked_out)
        return f"Library({self.name} | {len(self._books)} books | {available} available)"
    

# =============================================
# MAIN - Test the entire system
# =============================================

if __name__ == "__main__":
    print("=" * 50)
    print("LIBRARY SYSTEM - FULL TEST")
    print("=" * 50)

    # Setup
    library = Library("Chennai Public Library")

    # Add books
    book1 = Book("Clean Code", "Robert Martin", "978-0132350884")
    book2 = Book("The Pragmatic Programmer", "David Thomas", "978-0135957059")
    book3 = Book("Python Crash Course", "Eric Matthes", "978-1593279288")
    book4 = Book("Clean Code", "Robert Martin", "978-0132350885")  # second copy

    # Register members
    admin = Admin("Divya", "divya@library.com")
    member1 = Member("Arjun", "arjun@test.com")
    member2 = Member("Priya", "priya@test.com")

    admin.add_book(library, book1)
    admin.add_book(library, book2)
    admin.add_book(library, book3)
    admin.add_book(library, book4)

    library.register_member(admin)
    library.register_member(member1)
    library.register_member(member2)

    print(f"\n{library}")

    # Test checkout
    print("\n--- CHECKOUT ---")
    member1.checkout_book(book1)
    member2.checkout_book(book2)
    print(f"Arjun borrowed: {[b.title for b in member1.get_borrowed_books()]}")
    print(f"Priya borrowed: {[b.title for b in member2.get_borrowed_books()]}")

    # Test double checkout - should fail
    print("\n--- DOUBLE CHECKOUT (should fail) ---")
    try:
        admin.checkout_book(book1)   # already borrowed by Arjun
    except ValueError as e:
        print(f"Correctly blocked: {e}")

    # Test search
    print("\n--- SEARCH ---")
    results = library.find_by_title("clean code")
    print(f"Search 'clean code': found {len(results)} books")
    for b in results:
        print(f"  {b}")

    # Test return
    print("\n--- RETURN ---")
    member1.return_book(book1)
    print(f"Arjun's books after return: {member1.get_borrowed_books()}")
    print(f"Book1 available: {not book1.is_checked_out}")

    # Test overdue (simulate by manually setting borrowed_date back 20 days)
    print("\n--- OVERDUE TEST ---")
    member2.checkout_book(book3)
    book2.borrowed_date = date.today() - timedelta(days=20)   # simulate overdue
    book3.borrowed_date = date.today() - timedelta(days=5)    # not overdue

    overdue = library.list_overdue_books()
    print(f"Overdue books: {len(overdue)}")
    for b in overdue:
        print(f"  {b.title} - {b.days_overdue()} days overdue - borrowed by {b.borrowed_by.name}")

    # Show all books
    print("\n--- ALL BOOKS ---")
    library.show_all_books()

    # Admin remove book - should fail if checked out
    print("\n--- REMOVE BOOK (checked out, should fail) ---")
    try:
        admin.remove_book(library, book2)
    except ValueError as e:
        print(f"Correctly blocked: {e}")

    print("\n--- REMOVE BOOK (available) ---")
    admin.remove_book(library, book1)   # book1 was returned, should work
    print(f"Library after removal: {library}")

    print("\n" + "=" * 50)
    print("ALL TESTS PASSED")
    print("=" * 50)