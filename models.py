import os
from datetime import datetime
import json

class Book:
    def __init__(self, book_id, title, author, isbn, status="Available", borrowed_at=None, returned_at=None):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.isbn = isbn
        self.status = status
        self.borrowed_at = borrowed_at
        self.returned_at = returned_at
        
    def to_dict(self):
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "status": self.status,
            "borrowed_at": self.borrowed_at.isoformat() if isinstance(self.borrowed_at, datetime) else self.borrowed_at,
            "returned_at": self.returned_at.isoformat() if isinstance(self.returned_at, datetime) else self.returned_at
        }

class Member:
    MAX_BOOKS = 3

    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email
        self.borrowed_books = []

    def request_book(self, book):
        if len(self.borrowed_books) >= self.MAX_BOOKS:
            return False, f"Request denied. You have reached your limit of {self.MAX_BOOKS} books."

        if book.status == "Available":
            book.status = "Pending Approval"
            return True, f"{book.title} has been requested. Waiting for approval"

        else:
            return False, f"{book.title} is not available"

    def to_dict(self):
        borrowed_formatted = []
        for book in self.borrowed_books:
            borrowed_formatted.append({
                "book_id": book.book_id,
                "date_borrowed": book.borrowed_at.isoformat() if isinstance(book.borrowed_at, datetime) else book.borrowed_at,
                "date_returned": book.returned_at.isoformat() if isinstance(book.returned_at, datetime) else book.returned_at
            })

        return {
            "role": "member",
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "borrowed_books": borrowed_formatted
        }

class Librarian(Member):
    def __init__(self, id, name, email, department):
        super().__init__(id, name, email)
        self.department = department

    def add_book(self, library, book_id, title, author, isbn):
        new_book = Book(book_id, title, author, isbn)
        library.catalog.append(new_book)
        return new_book, f"Librarian {self.name} added '{title}' by {author} to the catalog."

    def approve_request(self, member, book):
        if len(member.borrowed_books) >= member.MAX_BOOKS:
            book.status = "Available" 
            return False, f"Approval denied. {member.name} has hit their maximum limit of {member.MAX_BOOKS} books."

        if book.status == "Pending Approval":
            book.status = "Borrowed"
            member.borrowed_books.append(book)
            book.borrowed_at = datetime.now()
            book.returned_at = None
            return True, f"Librarian {self.name} APPROVED the request for '{book.title}' by {member.name}."

        else:
            return False, f"Cannot approve. '{book.title}' is not pending approval."
            
    def to_dict(self):
        data = super().to_dict()
        data["role"] = "librarian"
        data["department"] = self.department

        data.pop("borrowed_books", None)
        return data

class Library:
    def __init__(self):
        self.catalog = []
        self.users = []

    def load_database(self, books_file="database/books.json", users_file="database/users.json"):
        try:
            with open(books_file, "r") as bf:
                books_data = json.load(bf)
                self.catalog = [Book(**book) for book in books_data]
        except FileNotFoundError:
            self.catalog = []

        try:
            with open(users_file, "r") as uf:
                users_data = json.load(uf)
                for u in users_data:
                    if u["role"] == "librarian":
                        user_obj = Librarian(u["id"], u["name"], u["email"], u["department"])
                    else:
                        user_obj = Member(u["id"], u["name"], u["email"])
                    
                    if "borrowed_books" in u:
                        user_obj.borrowed_books = [b for b in self.catalog if b.book_id in u["borrowed_books"]]
                    
                    self.users.append(user_obj)
        except FileNotFoundError:
            self.users = []

        return True, "Database synced successfully."

    def save_database(self, books_file="database/books.json", users_file="database/users.json"):
        """Saves current state to JSON files (Call this after any mutation/change)."""
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(books_file), exist_ok=True)
        
        with open(books_file, "w") as bf:
            json.dump([book.to_dict() for book in self.catalog], bf, indent=4)
            
        with open(users_file, "w") as uf:
            json.dump([user.to_dict() for user in self.users], uf, indent=4)
            
        return True, "Changes saved to disk."
    
    def register_user(self, role, user_id, name, email, department=None):
        for existing_user in self.users:
            if existing_user.email == email:
                return False, f"Registration failed. Email '{email}' is already registered."
            if existing_user.id == user_id:
                return False, f"Registration failed. User ID '{user_id}' is already taken."

        if role.lower() == "librarian":
            if not department:
                return False, "Registration failed. Librarians require a department."
            new_user = Librarian(user_id, name, email, department)
        elif role.lower() == "member":
            new_user = Member(user_id, name, email)
        else:
            return False, "Registration failed. Invalid user type. Must be 'member' or 'librarian'."

        self.users.append(new_user)
        self.save_database()
        return True, f"Successfully registered {role.capitalize()}: {name}."
    
    def show_available_books(self):
        available_books = [book for book in self.catalog if book.status == "Available"]
        frontend_data = [book.to_dict() for book in available_books]
        return frontend_data
