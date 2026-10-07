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
