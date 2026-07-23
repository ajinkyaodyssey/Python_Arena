# Library Management System

A Python OOP project built as part of the SDET 90-Day Training Plan.

## What It Demonstrates
- Classes and objects (Book, Member, Admin, Library)
- Inheritance (Admin extends Member)
- Encapsulation (_borrowed_books, _books are protected)
- Class attributes (_member_counter for auto-generated IDs)
- @property (overdue calculations)
- Object relationships (Book stores Member object, not just a name)

## How to Run
python3 library_system.py

## Classes
- Book: Represents a library book, tracks checkout status and borrowed date
- Member: Can borrow and return books, tracks their borrowed list
- Admin(Member): Inherits all Member abilities, can also add/remove books from library
- Library: Central manager, holds all books and members, provides search

## Operations
- Add book (Admin only)
- Remove book (Admin only, cannot remove if checked out)
- Checkout book (Member/Admin)
- Return book (Member/Admin)
- Search by title (case insensitive, returns all matching copies)
- List overdue books (books borrowed more than 14 days ago)