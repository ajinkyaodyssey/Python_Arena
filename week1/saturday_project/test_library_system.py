# week1/saturday_project/test_library_system.py
# Unit tests for LibrarySystem using pytest
# Run with: pytest week1/saturday_project/test_library_system.py -v

import pytest
from datetime import date, timedelta
from week1.saturday_project.library_system import Book, Member, Admin, Library


# =============================================
# FIXTURES — shared setup across tests
# =============================================

@pytest.fixture
def book():
    """A fresh available book for each test."""
    return Book("Clean Code", "Robert Martin", "978-0132350884")

@pytest.fixture
def member():
    """A fresh member for each test."""
    return Member("Arjun", "arjun@test.com")

@pytest.fixture
def another_member():
    """A second member for conflict tests."""
    return Member("Priya", "priya@test.com")

@pytest.fixture
def library():
    """A fresh library for each test."""
    return Library("Test Library")

@pytest.fixture
def admin():
    """A fresh admin for each test."""
    return Admin("Divya", "divya@library.com")

@pytest.fixture
def stocked_library(library, admin):
    """Library with 3 books already added."""
    book1 = Book("Clean Code", "Robert Martin", "ISBN-001")
    book2 = Book("Pragmatic Programmer", "David Thomas", "ISBN-002")
    book3 = Book("Python Crash Course", "Eric Matthes", "ISBN-003")
    admin.add_book(library, book1)
    admin.add_book(library, book2)
    admin.add_book(library, book3)
    return library, [book1, book2, book3]


# =============================================
# TEST 1: Book is available when created
# =============================================

def test_book_is_available_on_creation(book):
    assert book.is_checked_out == False
    assert book.borrowed_by is None
    assert book.borrowed_date is None


# =============================================
# TEST 2: Checkout sets correct state
# =============================================

def test_checkout_sets_correct_state(book, member):
    member.checkout_book(book)

    assert book.is_checked_out == True
    assert book.borrowed_by is member
    assert book.borrowed_date == date.today()
    assert book in member.get_borrowed_books()


# =============================================
# TEST 3: Double checkout raises ValueError
# =============================================

def test_double_checkout_raises_value_error(book, member, another_member):
    member.checkout_book(book)

    with pytest.raises(ValueError) as exc_info:
        another_member.checkout_book(book)

    assert "already checked out" in str(exc_info.value)


# =============================================
# TEST 4: Return book resets state correctly
# =============================================

def test_return_book_resets_state(book, member):
    member.checkout_book(book)
    member.return_book(book)

    assert book.is_checked_out == False
    assert book.borrowed_by is None
    assert book.borrowed_date is None
    assert book not in member.get_borrowed_books()


# =============================================
# TEST 5: Returning a book not checked out raises ValueError
# =============================================

def test_return_book_not_checked_out_raises_error(book):
    with pytest.raises(ValueError) as exc_info:
        book.return_book()

    assert "not currently checked out" in str(exc_info.value)


# =============================================
# TEST 6: Overdue detection works correctly
# =============================================

def test_book_is_overdue_after_14_days(book, member):
    member.checkout_book(book)
    # Simulate borrowing 20 days ago
    book.borrowed_date = date.today() - timedelta(days=20)

    assert book.is_overdue() == True
    assert book.days_overdue() == 6   # 20 - 14 = 6 days overdue


def test_book_is_not_overdue_within_14_days(book, member):
    member.checkout_book(book)
    book.borrowed_date = date.today() - timedelta(days=10)

    assert book.is_overdue() == False
    assert book.days_overdue() == 0


# =============================================
# TEST 7: Library find_by_title is case insensitive
# =============================================

def test_find_by_title_case_insensitive(stocked_library):
    library, books = stocked_library

    results_lower = library.find_by_title("clean code")
    results_upper = library.find_by_title("CLEAN CODE")
    results_mixed = library.find_by_title("Clean Code")

    assert len(results_lower) == 1
    assert len(results_upper) == 1
    assert len(results_mixed) == 1
    assert results_lower[0].title == "Clean Code"


# =============================================
# TEST 8: Library add_book rejects duplicate ISBN
# =============================================

def test_add_book_raises_on_duplicate_isbn(library, admin):
    book1 = Book("Clean Code", "Robert Martin", "ISBN-SAME")
    book2 = Book("Clean Code Second Copy", "Robert Martin", "ISBN-SAME")

    admin.add_book(library, book1)

    with pytest.raises(ValueError) as exc_info:
        admin.add_book(library, book2)

    assert "already exists" in str(exc_info.value)


# =============================================
# TEST 9: Admin cannot remove a checked out book
# =============================================

def test_admin_cannot_remove_checked_out_book(library, admin, member):
    book = Book("Clean Code", "Robert Martin", "ISBN-001")
    admin.add_book(library, book)
    member.checkout_book(book)

    with pytest.raises(ValueError) as exc_info:
        admin.remove_book(library, book)

    assert "checked out" in str(exc_info.value)
    assert book in library._books   # book still in library


# =============================================
# TEST 10: list_overdue_books returns correct books
# =============================================

def test_list_overdue_books(stocked_library, member, another_member):
    library, books = stocked_library
    book1, book2, book3 = books

    # Check out two books
    member.checkout_book(book1)
    another_member.checkout_book(book2)

    # Make book1 overdue, book2 not overdue
    book1.borrowed_date = date.today() - timedelta(days=20)
    book2.borrowed_date = date.today() - timedelta(days=5)

    overdue = library.list_overdue_books()

    assert len(overdue) == 1
    assert book1 in overdue
    assert book2 not in overdue
    assert book3 not in overdue   # never checked out