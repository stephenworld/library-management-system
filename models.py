import os
import json
from datetime import datetime
from abc import ABC, abstractmethod


class Book:
    def __init__(self, book_id, title, author, isbn, status="Available", borrowed_at=None, returned_at=None):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.isbn = isbn
        self.status = status
        self.borrowed_at = (
            datetime.fromisoformat(borrowed_at) if isinstance(borrowed_at, str) else borrowed_at
        )
        self.returned_at = (
            datetime.fromisoformat(returned_at) if isinstance(returned_at, str) else returned_at
        )

    def to_dict(self):
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "status": self.status,
            "borrowed_at": self.borrowed_at.isoformat() if self.borrowed_at else None,
            "returned_at": self.returned_at.isoformat() if self.returned_at else None,
        }


class User(ABC):
    """Abstract base class representing any library system user."""

    def __init__(self, user_id, name, email):
        self.id = user_id
        self.name = name
        self.email = email

    @abstractmethod
    def to_dict(self):
        """Base representation for all users; extended by child classes."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
        }


class Member(User):
    MAX_BOOKS = 3

    def __init__(self, user_id, name, email):
        super().__init__(user_id, name, email)
        self.borrowed_books = []

    def request_book(self, book):
        if len(self.borrowed_books) >= self.MAX_BOOKS:
            return False, f"Request denied. You have reached your limit of {self.MAX_BOOKS} books."

        if book.status == "Available":
            book.status = "Pending Approval"
            return True, f"'{book.title}' requested. Waiting for approval."
        
        return False, f"'{book.title}' is not available."

    def to_dict(self):
        data = super().to_dict()
        data["role"] = "member"
        # Store borrowed records with foreign key `book_id`
        data["borrowed_books"] = [
            {
                "book_id": book.book_id,
                "date_borrowed": book.borrowed_at.isoformat() if book.borrowed_at else None,
                "date_returned": book.returned_at.isoformat() if book.returned_at else None,
            }
            for book in self.borrowed_books
        ]
        return data


class Librarian(User):
    def __init__(self, user_id, name, email, department):
        super().__init__(user_id, name, email)
        self.department = department

    def add_book(self, library, book_id, title, author, isbn):
        new_book = Book(book_id, title, author, isbn)
        library.catalog.append(new_book)
        return new_book, f"Librarian {self.name} added '{title}' by {author}."

    def approve_request(self, member, book):
        if len(member.borrowed_books) >= member.MAX_BOOKS:
            book.status = "Available"
            return False, f"Approval denied. {member.name} has hit the maximum limit of {member.MAX_BOOKS} books."

        if book.status == "Pending Approval":
            book.status = "Borrowed"
            member.borrowed_books.append(book)
            book.borrowed_at = datetime.now()
            book.returned_at = None
            return True, f"Librarian {self.name} APPROVED request for '{book.title}' by {member.name}."

        return False, f"Cannot approve. '{book.title}' is not pending approval."

    def to_dict(self):
        data = super().to_dict()
        data["role"] = "librarian"
        data["department"] = self.department
        return data


class Library:
    def __init__(self):
        self.catalog = []
        self.users = []

    def load_database(self, books_file="database/books.json", users_file="database/users.json"):
        # 1. Load books into a lookup dictionary for fast O(1) matching
        self.catalog = []
        catalog_lookup = {}

        try:
            with open(books_file, "r") as bf:
                books_data = json.load(bf)
                for item in books_data:
                    book_obj = Book(**item)
                    self.catalog.append(book_obj)
                    catalog_lookup[book_obj.book_id] = book_obj
        except FileNotFoundError:
            self.catalog = []

        # 2. Load users and reconnect references
        self.users = []
        try:
            with open(users_file, "r") as uf:
                users_data = json.load(uf)
                for u in users_data:
                    role = u.get("role", "member")

                    if role == "librarian":
                        user_obj = Librarian(u["id"], u["name"], u["email"], u["department"])
                    else:
                        user_obj = Member(u["id"], u["name"], u["email"])
                        
                        # Fix: Extract `book_id` whether stored as dict or raw ID
                        raw_borrowed = u.get("borrowed_books", [])
                        borrowed_ids = [
                            entry["book_id"] if isinstance(entry, dict) else entry 
                            for entry in raw_borrowed
                        ]
                        user_obj.borrowed_books = [
                            catalog_lookup[b_id] for b_id in borrowed_ids if b_id in catalog_lookup
                        ]

                    self.users.append(user_obj)
        except FileNotFoundError:
            self.users = []

        return self.catalog, self.users, "Database synced successfully."

    def save_database(self, books_file="database/books.json", users_file="database/users.json"):
        os.makedirs(os.path.dirname(books_file), exist_ok=True)
        os.makedirs(os.path.dirname(users_file), exist_ok=True)

        with open(books_file, "w") as bf:
            json.dump([book.to_dict() for book in self.catalog], bf, indent=4)

        with open(users_file, "w") as uf:
            json.dump([user.to_dict() for user in self.users], uf, indent=4)

        return True, "Changes saved to disk."

    def register_user(self, role, user_id, name, email, department=None):
        for existing in self.users:
            if existing.email == email:
                return False, f"Registration failed. Email '{email}' is already registered."
            if existing.id == user_id:
                return False, f"Registration failed. User ID '{user_id}' is already taken."

        role_clean = role.lower()
        if role_clean == "librarian":
            if not department:
                return False, "Registration failed. Librarians require a department."
            new_user = Librarian(user_id, name, email, department)
        elif role_clean == "member":
            new_user = Member(user_id, name, email)
        else:
            return False, "Registration failed. Invalid role. Must be 'member' or 'librarian'."

        self.users.append(new_user)
        self.save_database()
        return True, f"Successfully registered {role.capitalize()}: {name}."

    def show_available_books(self):
        return [b.to_dict() for b in self.catalog if b.status == "Available"]
