# week1/saturday_project/library_system.py
# LibrarySystem with full type hints
# Refactored as part of Week 1 Saturday project

from datetime import date, timedelta
from typing import Optional


class Book:
    LOAN_PERIOD_DAYS: int = 14

    def __init__(self, title: str, author: str, isbn: str) -> None:
        self.title: str = title
        self.author: str = author
        self.isbn: str = isbn
        self.is_checked_out: bool = False
        self.borrowed_by: Optional["Member"] = None
        self.borrowed_date: Optional[date] = None

    def checkout(self, member: "Member") -> None:
        if self.is_checked_out:
            raise ValueError(
                f"'{self.title}' is already checked out by "
                f"{self.borrowed_by.name}"
            )
        self.is_checked_out = True
        self.borrowed_by = member
        self.borrowed_date = date.today()

    def return_book(self) -> None:
        if not self.is_checked_out:
            raise ValueError(f"'{self.title}' is not currently checked out")
        self.is_checked_out = False
        self.borrowed_by = None
        self.borrowed_date = None

    def is_overdue(self) -> bool:
        if not self.is_checked_out or self.borrowed_date is None:
            return False
        return (date.today() - self.borrowed_date).days > self.LOAN_PERIOD_DAYS

    def days_overdue(self) -> int:
        if not self.is_overdue():
            return 0
        return (date.today() - self.borrowed_date).days - self.LOAN_PERIOD_DAYS

    def __str__(self) -> str:
        if self.is_checked_out:
            days = (date.today() - self.borrowed_date).days
            return (
                f"'{self.title}' by {self.author} "
                f"[CHECKED OUT by {self.borrowed_by.name} "
                f"— {days} day(s) ago"
                f"{' OVERDUE' if self.is_overdue() else ''}]"
            )
        return f"'{self.title}' by {self.author} [ISBN: {self.isbn}] — Available"

    def __repr__(self) -> str:
        return f"Book(title={self.title!r}, isbn={self.isbn!r})"


class Member:
    _member_counter: int = 0

    def __init__(self, name: str, email: str) -> None:
        Member._member_counter += 1
        self.member_id: str = f"MEM{Member._member_counter:04d}"
        self.name: str = name
        self.email: str = email
        self._borrowed_books: list[Book] = []

    def checkout_book(self, book: Book) -> None:
        book.checkout(self)
        self._borrowed_books.append(book)

    def return_book(self, book: Book) -> None:
        book.return_book()
        self._borrowed_books.remove(book)

    def get_borrowed_books(self) -> list[Book]:
        return self._borrowed_books

    def __str__(self) -> str:
        return (
            f"Member({self.member_id} | {self.name} | "
            f"{len(self._borrowed_books)} book(s) borrowed)"
        )

    def __repr__(self) -> str:
        return f"Member(member_id={self.member_id!r}, name={self.name!r})"


class Admin(Member):

    def __init__(self, name: str, email: str) -> None:
        super().__init__(name, email)
        self.member_id = self.member_id.replace("MEM", "ADM")
        self._added_books: list[Book] = []

    def add_book(self, library: "Library", book: Book) -> None:
        library.add_book(book)
        self._added_books.append(book)

    def remove_book(self, library: "Library", book: Book) -> None:
        if book.is_checked_out:
            raise ValueError(
                f"Cannot remove '{book.title}' — currently checked out"
            )
        library.remove_book(book)

    def __str__(self) -> str:
        return (
            f"Admin({self.member_id} | {self.name} | "
            f"{len(self._added_books)} book(s) added)"
        )


class Library:

    def __init__(self, name: str) -> None:
        self.name: str = name
        self._books: list[Book] = []
        self._members: list[Member] = []

    def add_book(self, book: Book) -> None:
        existing_isbns = [b.isbn for b in self._books]
        if book.isbn in existing_isbns:
            raise ValueError(f"Book with ISBN {book.isbn} already exists")
        self._books.append(book)

    def remove_book(self, book: Book) -> None:
        if book not in self._books:
            raise ValueError(f"'{book.title}' is not in this library")
        self._books.remove(book)

    def register_member(self, member: Member) -> None:
        self._members.append(member)

    def find_by_title(self, title: str) -> list[Book]:
        title_lower = title.lower()
        return [b for b in self._books if title_lower in b.title.lower()]

    def find_by_isbn(self, isbn: str) -> Optional[Book]:
        for book in self._books:
            if book.isbn == isbn:
                return book
        return None

    def list_overdue_books(self) -> list[Book]:
        return [b for b in self._books if b.is_overdue()]

    def show_all_books(self) -> None:
        print(f"\n{self.name} — All Books ({len(self._books)} total):")
        for book in self._books:
            print(f"  {book}")

    def __str__(self) -> str:
        available = sum(1 for b in self._books if not b.is_checked_out)
        return (
            f"Library({self.name} | "
            f"{len(self._books)} books | "
            f"{available} available)"
        )


if __name__ == "__main__":
    print("=" * 50)
    print("LIBRARY SYSTEM — INTEGRATION TEST")
    print("=" * 50)

    library = Library("Chennai Public Library")

    book1 = Book("Clean Code", "Robert Martin", "978-0132350884")
    book2 = Book("The Pragmatic Programmer", "David Thomas", "978-0135957059")
    book3 = Book("Python Crash Course", "Eric Matthes", "978-1593279288")
    book4 = Book("Clean Code", "Robert Martin", "978-0132350885")

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

    member1.checkout_book(book1)
    member2.checkout_book(book2)

    try:
        admin.checkout_book(book1)
    except ValueError as e:
        print(f"Correctly blocked double checkout: {e}")

    results = library.find_by_title("clean code")
    print(f"\nSearch 'clean code': {len(results)} found")

    member1.return_book(book1)
    print(f"After return — book1 available: {not book1.is_checked_out}")

    book2.borrowed_date = date.today() - timedelta(days=20)
    overdue = library.list_overdue_books()
    print(f"\nOverdue books: {len(overdue)}")
    for b in overdue:
        print(f"  {b.title} — {b.days_overdue()} days overdue")

    library.show_all_books()
    print("\n" + "=" * 50)
    print("ALL SCENARIOS PASSED")
    print("=" * 50)