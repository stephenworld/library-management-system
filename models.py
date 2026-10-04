import json
import os
import tempfile
from datetime import datetime
from pathlib import Path


class LibraryError(Exception):
    """Base error for expected library operations and data problems."""


class NotFoundError(LibraryError):
    pass


class ConflictError(LibraryError):
    pass


class LibraryDataError(LibraryError):
    pass


class Book:
    def __init__(
        self, book_id, title, author, isbn, status="Available",
        borrowed_at=None, returned_at=None,
    ):
        self.book_id = str(book_id)
        self.title = title
        self.author = author
        self.isbn = isbn
        self.status = status
        self.borrowed_at = self._parse_date(borrowed_at)
        self.returned_at = self._parse_date(returned_at)

    @staticmethod
    def _parse_date(value):
        return datetime.fromisoformat(value) if isinstance(value, str) else value

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


class User:
    def __init__(self, user_id, name, email):
        self.id = str(user_id)
        self.name = name
        self.email = email

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email}


class Member(User):
    MAX_BOOKS = 3

    def __init__(self, user_id, name, email):
        super().__init__(user_id, name, email)
        self.borrowed_books = []

    def request_book(self, library, book):
        return library.request_book(self.id, book.book_id)

    def to_dict(self):
        data = super().to_dict()
        data["role"] = "member"
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
        return library.add_book(book_id, title, author, isbn)

    def to_dict(self):
        data = super().to_dict()
        data["role"] = "librarian"
        data["department"] = self.department
        return data


class BookRequest:
    def __init__(
        self, request_id, user_id, book_id, status, requested_at=None,
        approved_at=None, returned_at=None,
    ):
        self.request_id = int(request_id)
        self.user_id = str(user_id)
        self.book_id = str(book_id)
        self.status = status
        self.requested_at = requested_at or datetime.now().isoformat()
        self.approved_at = approved_at
        self.returned_at = returned_at

    def to_dict(self):
        return {
            "request_id": self.request_id,
            "user_id": self.user_id,
            "book_id": self.book_id,
            "status": self.status,
            "requested_at": self.requested_at,
            "approved_at": self.approved_at,
            "returned_at": self.returned_at,
        }


class Library:
    def __init__(self):
        self.catalog = []
        self.users = []
        self.requests = []
        database_directory = Path(__file__).resolve().parent / "database"
        self.books_file = database_directory / "books.json"
        self.users_file = database_directory / "users.json"
        self.requests_file = database_directory / "requests.json"

    def load_database(
        self, books_file=None, users_file=None, requests_file=None
    ):
        if books_file is not None:
            self.books_file = Path(books_file)
        if users_file is not None:
            self.users_file = Path(users_file)
        if requests_file is not None:
            self.requests_file = Path(requests_file)

        updated_library = Library()
        updated_library.books_file = self.books_file
        updated_library.users_file = self.users_file
        updated_library.requests_file = self.requests_file
        updated_library._load_database()

        self.catalog = updated_library.catalog
        self.users = updated_library.users
        self.requests = updated_library.requests
        return self.catalog, self.users, "Database synced successfully."

    def _load_database(self):
        book_records = self._read_json(self.books_file, [])
        user_records = self._read_json(self.users_file, [])
        request_data = self._read_json(self.requests_file, {"requests": []})
        if isinstance(request_data, dict):
            request_records = request_data.get("requests", [])
        elif isinstance(request_data, list):
            request_records = request_data
        else:
            raise LibraryDataError("requests.json must contain a request list")

        self.catalog = [Book(**record) for record in book_records]
        books_by_id = self._unique_lookup(self.catalog, "book_id", "book")
        self.users = []
        raw_borrowed_by_user = {}
        for record in user_records:
            role = record.get("role", "member").lower()
            if role == "librarian":
                user = Librarian(
                    record["id"], record["name"], record["email"],
                    record.get("department", ""),
                )
            elif role == "member":
                user = Member(record["id"], record["name"], record["email"])
                raw_borrowed_by_user[user.id] = record.get("borrowed_books", [])
            else:
                raise LibraryDataError(f"Unknown user role {role!r} for user {record.get('id')!r}")
            self.users.append(user)
        users_by_id = self._unique_lookup(self.users, "id", "user")

        borrowed_book_ids = set()
        active_loans = set()
        for user_id, records in raw_borrowed_by_user.items():
            member = users_by_id[user_id]
            for record in records:
                borrowed_id = str(record["book_id"] if isinstance(record, dict) else record)
                book = books_by_id.get(borrowed_id)
                if book is None:
                    raise LibraryDataError(
                        f"Member {user_id!r} references missing book {borrowed_id!r}"
                    )
                if borrowed_id in borrowed_book_ids:
                    raise LibraryDataError(f"Book {borrowed_id!r} is linked to multiple members")
                borrowed_book_ids.add(borrowed_id)
                active_loans.add((member.id, borrowed_id))
                if isinstance(record, dict) and record.get("date_borrowed"):
                    book.borrowed_at = Book._parse_date(record["date_borrowed"])
                if isinstance(record, dict) and record.get("date_returned"):
                    book.returned_at = Book._parse_date(record["date_returned"])
                member.borrowed_books.append(book)

        self.requests = []
        seen_request_ids = set()
        for index, record in enumerate(request_records, 1):
            status = record.get("status", "pending").strip().casefold()
            if status == "pending approval":
                status = "pending"
            if status not in {"pending", "approved", "returned", "rejected"}:
                raise LibraryDataError(f"Unknown request status {record.get('status')!r}")
            request = BookRequest(
                record.get("request_id", index), record["user_id"], record["book_id"],
                status, record.get("requested_at"), record.get("approved_at"),
                record.get("returned_at"),
            )
            if request.returned_at and request.status == "approved":
                request.status = "returned"
            if request.user_id not in users_by_id:
                raise LibraryDataError(f"Request references missing user {request.user_id!r}")
            if not isinstance(users_by_id[request.user_id], Member):
                raise LibraryDataError(f"Request owner {request.user_id!r} is not a member")
            if request.book_id not in books_by_id:
                raise LibraryDataError(f"Request references missing book {request.book_id!r}")
            if request.request_id in seen_request_ids:
                raise LibraryDataError(f"Duplicate request ID {request.request_id!r}")
            seen_request_ids.add(request.request_id)
            self.requests.append(request)

        self._reconcile_request_history(active_loans, books_by_id)

        pending_by_book = set()
        for request in self.requests:
            if request.status == "pending":
                if request.book_id in pending_by_book:
                    raise LibraryDataError(
                        f"Book {request.book_id!r} has more than one pending request"
                    )
                if request.book_id in borrowed_book_ids:
                    raise LibraryDataError(
                        f"Book {request.book_id!r} is both pending and borrowed"
                    )
                pending_by_book.add(request.book_id)

        for book in self.catalog:
            original_status = book.status.casefold()
            if book.book_id in borrowed_book_ids:
                book.status = "Borrowed"
            elif book.book_id in pending_by_book:
                book.status = "Pending Approval"
            elif original_status in {"borrowed", "pending approval"}:
                raise LibraryDataError(
                    f"Book {book.book_id!r} is marked {book.status!r} without a matching record"
                )
            else:
                book.status = "Available"

        return self.catalog, self.users, "Database synced successfully."

    def _reconcile_request_history(self, active_loans, books_by_id):
        approved_by_loan = {}
        for request in self.requests:
            if request.status == "approved":
                key = (request.user_id, request.book_id)
                approved_by_loan.setdefault(key, []).append(request)

        next_request_id = max((request.request_id for request in self.requests), default=0) + 1
        for member_id, book_id in active_loans:
            key = (member_id, book_id)
            if key in approved_by_loan:
                continue
            book = books_by_id[book_id]
            borrowed_at = book.borrowed_at.isoformat() if book.borrowed_at else None
            request = BookRequest(
                next_request_id, member_id, book_id, "approved",
                requested_at=borrowed_at,
                approved_at=borrowed_at,
            )
            self.requests.append(request)
            approved_by_loan[key] = [request]
            next_request_id += 1

        for (member_id, book_id), requests in approved_by_loan.items():
            current_request = max(requests, key=lambda request: request.request_id)
            book = books_by_id[book_id]
            if current_request.approved_at is None and book.borrowed_at:
                current_request.approved_at = book.borrowed_at.isoformat()
            if (member_id, book_id) in active_loans:
                for request in requests:
                    if request is not current_request:
                        request.status = "returned"
                continue

            for request in requests:
                request.status = "returned"
            if current_request.returned_at is None and book.returned_at:
                current_request.returned_at = book.returned_at.isoformat()

    def save_database(self):
        documents = (
            (self.books_file, [book.to_dict() for book in self.catalog]),
            (self.users_file, [user.to_dict() for user in self.users]),
            (self.requests_file, {"requests": [request.to_dict() for request in self.requests]}),
        )
        self._write_json_documents(documents)
        return True, "Changes saved to JSON files."

    def register_user(self, role, user_id, name, email, department=None):
        role_clean = role.strip().lower()
        email_key = email.strip().casefold()
        for existing in self.users:
            if existing.email.strip().casefold() == email_key:
                return False, f"Registration failed. Email '{email}' is already registered."
            if existing.id == str(user_id):
                return False, f"Registration failed. User ID '{user_id}' is already taken."

        if role_clean == "librarian":
            if not department:
                return False, "Registration failed. Librarians require a department."
            new_user = Librarian(user_id, name, email, department)
        elif role_clean == "member":
            new_user = Member(user_id, name, email)
        else:
            return False, "Registration failed. Invalid role. Must be 'member' or 'librarian'."

        self.users.append(new_user)
        try:
            self.save_database()
        except LibraryDataError:
            self.users.remove(new_user)
            raise
        return True, f"Successfully registered {role_clean.capitalize()}: {name}."

    def add_book(self, book_id, title, author, isbn):
        book_id = str(book_id)
        if any(book.book_id == book_id for book in self.catalog):
            raise ConflictError(f"Book ID {book_id!r} already exists")
        new_book = Book(book_id, title, author, isbn)
        self.catalog.append(new_book)
        try:
            self.save_database()
        except LibraryDataError:
            self.catalog.remove(new_book)
            raise
        return new_book, f"Added '{title}' by {author}."

    def request_book(self, member_id, book_id):
        member = self._find_member(member_id)
        book = self._find_book(book_id)
        if book.status != "Available":
            return False, f"'{book.title}' is not available."
        open_requests = sum(
            request.user_id == member.id and request.status == "pending"
            for request in self.requests
        )
        if len(member.borrowed_books) + open_requests >= Member.MAX_BOOKS:
            return False, f"Request denied. You have reached your limit of {Member.MAX_BOOKS} books."

        request_id = max((request.request_id for request in self.requests), default=0) + 1
        request = BookRequest(request_id, member.id, book.book_id, "pending")
        self.requests.append(request)
        book.status = "Pending Approval"
        try:
            self.save_database()
        except LibraryDataError:
            self.requests.remove(request)
            book.status = "Available"
            raise
        return True, f"'{book.title}' requested. Waiting for approval."

    def list_pending_requests(self):
        return [request for request in self.requests if request.status == "pending"]

    def approve_request(self, request_id):
        request = self._find_request(request_id)
        if request.status != "pending":
            return False, "Request is no longer pending."
        member = self._find_member(request.user_id)
        book = self._find_book(request.book_id)
        if len(member.borrowed_books) >= Member.MAX_BOOKS:
            return False, f"Approval denied. {member.name} has reached the book limit."

        old_borrowed_at = book.borrowed_at
        old_returned_at = book.returned_at
        old_approved_at = request.approved_at
        old_request_returned_at = request.returned_at
        approved_at = datetime.now().isoformat()
        request.status = "approved"
        request.approved_at = approved_at
        request.returned_at = None
        member.borrowed_books.append(book)
        book.status = "Borrowed"
        book.borrowed_at = datetime.fromisoformat(approved_at)
        book.returned_at = None
        try:
            self.save_database()
        except LibraryDataError:
            request.status = "pending"
            request.approved_at = old_approved_at
            request.returned_at = old_request_returned_at
            member.borrowed_books.remove(book)
            book.status = "Pending Approval"
            book.borrowed_at = old_borrowed_at
            book.returned_at = old_returned_at
            raise
        return True, f"Approved '{book.title}' for {member.name}."

    def reject_request(self, request_id):
        request = self._find_request(request_id)
        if request.status != "pending":
            return False, "Request is no longer pending."
        book = self._find_book(request.book_id)
        request.status = "rejected"
        book.status = "Available"
        try:
            self.save_database()
        except LibraryDataError:
            request.status = "pending"
            book.status = "Pending Approval"
            raise
        return True, f"Rejected request for '{book.title}'."

    def return_book(self, member_id, book_id):
        member = self._find_member(member_id)
        book = next((item for item in member.borrowed_books if item.book_id == str(book_id)), None)
        if book is None:
            return False, "You do not have that book checked out."
        request = next(
            (
                item for item in sorted(
                    self.requests, key=lambda entry: entry.request_id, reverse=True
                )
                if item.user_id == member.id
                and item.book_id == book.book_id
                and item.status == "approved"
                and item.returned_at is None
            ),
            None,
        )
        if request is None:
            raise LibraryDataError(
                f"No active checkout record exists for member {member.id!r} and book {book.book_id!r}"
            )
        member.borrowed_books.remove(book)
        old_status = book.status
        old_returned_at = book.returned_at
        returned_at = datetime.now().isoformat()
        book.status = "Available"
        book.returned_at = datetime.fromisoformat(returned_at)
        request.status = "returned"
        request.returned_at = returned_at
        try:
            self.save_database()
        except LibraryDataError:
            member.borrowed_books.append(book)
            book.status = old_status
            book.returned_at = old_returned_at
            request.status = "approved"
            request.returned_at = None
            raise
        return True, f"Returned '{book.title}'."

    def show_available_books(self):
        return [book.to_dict() for book in self.catalog if book.status == "Available"]

    def _find_member(self, member_id):
        for user in self.users:
            if user.id == str(member_id) and isinstance(user, Member):
                return user
        raise NotFoundError(f"Member {member_id!r} was not found")

    def _find_book(self, book_id):
        for book in self.catalog:
            if book.book_id == str(book_id):
                return book
        raise NotFoundError(f"Book {book_id!r} was not found")

    def _find_request(self, request_id):
        for request in self.requests:
            if request.request_id == int(request_id):
                return request
        raise NotFoundError(f"Request {request_id!r} was not found")

    @staticmethod
    def _unique_lookup(records, attribute, label):
        lookup = {}
        for record in records:
            key = getattr(record, attribute)
            if key in lookup:
                raise LibraryDataError(f"Duplicate {label} ID {key!r}")
            lookup[key] = record
        return lookup

    @staticmethod
    def _read_json(path, default):
        try:
            with path.open("r", encoding="utf-8") as source:
                return json.load(source)
        except FileNotFoundError:
            return default
        except (json.JSONDecodeError, OSError) as error:
            raise LibraryDataError(f"Could not read {path}: {error}") from error

    @staticmethod
    def _write_json_documents(documents):
        originals = {}
        temporary_paths = {}
        try:
            for path, document in documents:
                path.parent.mkdir(parents=True, exist_ok=True)
                originals[path] = path.read_bytes() if path.exists() else None
                with tempfile.NamedTemporaryFile(
                    "w", encoding="utf-8", dir=path.parent,
                    prefix=f".{path.name}.", suffix=".tmp", delete=False,
                ) as temporary:
                    json.dump(document, temporary, indent=4)
                    temporary.write("\n")
                    temporary_paths[path] = Path(temporary.name)
            for path, temporary_path in temporary_paths.items():
                os.replace(temporary_path, path)
        except OSError as error:
            for path, original in originals.items():
                try:
                    if original is None:
                        path.unlink(missing_ok=True)
                    else:
                        path.write_bytes(original)
                except OSError:
                    pass
            raise LibraryDataError(f"Could not save JSON data: {error}") from error
        finally:
            for temporary_path in temporary_paths.values():
                temporary_path.unlink(missing_ok=True)