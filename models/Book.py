from datetime import datetime

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
