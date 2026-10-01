from datetime import datetime

class Book:
    def __init__(self, book_id, title, author, isbn):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.isbn = isbn
        self.status = "Available"
        self.borrowed_at = None
        self.returned_at = None

    def to_dict(self):
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "status": self.status,
            "borrowed_at": self.borrowed_at,
            "returned_at": self.returned_at
        }

class Library:
    def __init__(self):
        self.catalog = []

    def show_available_books(self):
        available_books = [book for book in self.catalog if book.status == "Available"]
        frontend_data = [book.to_dict() for book in available_books]

        return frontend_data

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

