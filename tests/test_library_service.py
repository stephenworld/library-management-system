import tempfile
import unittest
from pathlib import Path

from models import Library, Member


class LibraryWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        root = Path(self.temporary_directory.name)
        self.library = Library()
        self.books_file = root / "books.json"
        self.users_file = root / "users.json"
        self.requests_file = root / "requests.json"
        self.library.load_database(self.books_file, self.users_file, self.requests_file)
        self.library.register_user("member", "001", "Member One", "member@example.com")
        self.library.register_user(
            "librarian", "002", "Librarian One", "librarian@example.com", "Library"
        )
        self.member = self.library.users[0]
        self.librarian = self.library.users[1]

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_repeated_checkouts_keep_separate_history_after_reload(self):
        book, _ = self.library.add_book("001", "Example Book", "Example Author", "1234567890")
        for _ in range(2):
            requested, _ = self.member.request_book(self.library, book)
            self.assertTrue(requested)

            reloaded = Library()
            books, users, _ = reloaded.load_database(
                self.books_file, self.users_file, self.requests_file
            )
            request = next(
                request for request in reloaded.requests if request.status == "pending"
            )
            self.assertEqual(request.user_id, self.member.id)
            self.assertEqual(request.book_id, book.book_id)

            approved, _ = reloaded.approve_request(request.request_id)
            self.assertTrue(approved)
            self.assertEqual(books[0].status, "Borrowed")
            reloaded_member = next(user for user in users if isinstance(user, Member))
            self.assertEqual(reloaded_member.borrowed_books[0].book_id, book.book_id)

            reloaded_again = Library()
            books, users, _ = reloaded_again.load_database(
                self.books_file, self.users_file, self.requests_file
            )
            member = next(user for user in users if isinstance(user, Member))
            returned, _ = reloaded_again.return_book(member.id, book.book_id)
            self.assertTrue(returned)
            self.assertEqual(books[0].status, "Available")
            self.assertEqual(member.borrowed_books, [])

            self.library = Library()
            _, users, _ = self.library.load_database(
                self.books_file, self.users_file, self.requests_file
            )
            self.member = next(user for user in users if isinstance(user, Member))
            book = self.library.catalog[0]

        self.assertEqual(len(self.library.requests), 2)
        self.assertTrue(all(request.status == "returned" for request in self.library.requests))
        self.assertTrue(all(request.approved_at for request in self.library.requests))
        self.assertTrue(all(request.returned_at for request in self.library.requests))
        self.assertNotEqual(
            self.library.requests[0].request_id,
            self.library.requests[1].request_id,
        )

    def test_pending_requests_count_toward_member_limit(self):
        books = [
            self.library.add_book(str(index), f"Book {index}", "Author", f"isbn-{index}")[0]
            for index in range(1, 5)
        ]
        for book in books[:3]:
            requested, _ = self.member.request_book(self.library, book)
            self.assertTrue(requested)

        requested, message = self.member.request_book(self.library, books[3])
        self.assertFalse(requested)
        self.assertIn("limit", message)


if __name__ == "__main__":
    unittest.main()