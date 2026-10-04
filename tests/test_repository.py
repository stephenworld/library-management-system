import json
import tempfile
import unittest
from pathlib import Path

from models import Library, LibraryDataError, Member
from utils import sync_data


class LibraryJsonTests(unittest.TestCase):
    def test_existing_json_files_load_request_owner_and_book_together(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            books_file = root / "books.json"
            users_file = root / "users.json"
            requests_file = root / "requests.json"
            books_file.write_text(
                '[{"book_id":"001","title":"Example","author":"Author",'
                '"isbn":"123","status":"Pending Approval"}]',
                encoding="utf-8",
            )
            users_file.write_text(
                '[{"id":"005","name":"Member","email":"member@example.com",'
                '"role":"member","borrowed_books":[]}]',
                encoding="utf-8",
            )
            requests_file.write_text(
                '{"requests":[{"user_id":"005","book_id":"001",'
                '"status":"Pending Approval","requested_at":"2024-06-10 12:00:00"}]}',
                encoding="utf-8",
            )

            library = Library()
            books, users, _ = library.load_database(books_file, users_file, requests_file)

            self.assertEqual(books[0].status, "Pending Approval")
            self.assertEqual(library.requests[0].user_id, "005")
            self.assertEqual(library.requests[0].book_id, "001")
            self.assertIsInstance(users[0], Member)

    def test_sync_refreshes_existing_menu_lists_and_logged_in_user_record(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            books_file = root / "books.json"
            users_file = root / "users.json"
            requests_file = root / "requests.json"
            books_file.write_text(
                json.dumps([{
                    "book_id": "001", "title": "Before sync", "author": "Author",
                    "isbn": "123", "status": "Available",
                }]),
                encoding="utf-8",
            )
            users_file.write_text(
                json.dumps([{
                    "id": "005", "name": "Before sync", "email": "member@example.com",
                    "role": "member", "borrowed_books": [],
                }]),
                encoding="utf-8",
            )
            requests_file.write_text('{"requests":[]}', encoding="utf-8")

            library = Library()
            books, users, _ = library.load_database(books_file, users_file, requests_file)
            old_member = users[0]
            refreshed_book_data = json.loads(books_file.read_text(encoding="utf-8"))
            refreshed_book_data[0]["title"] = "After sync"
            books_file.write_text(json.dumps(refreshed_book_data), encoding="utf-8")
            refreshed_user_data = json.loads(users_file.read_text(encoding="utf-8"))
            refreshed_user_data[0]["name"] = "After sync"
            users_file.write_text(json.dumps(refreshed_user_data), encoding="utf-8")

            sync_data(library, books, users)

            self.assertIs(library.catalog, books)
            self.assertIs(library.users, users)
            self.assertEqual(books[0].title, "After sync")
            self.assertEqual(users[0].name, "After sync")
            self.assertIsNot(users[0], old_member)

    def test_failed_sync_preserves_current_in_memory_state(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            books_file = root / "books.json"
            users_file = root / "users.json"
            requests_file = root / "requests.json"
            books_file.write_text(
                '[{"book_id":"001","title":"Example","author":"Author",'
                '"isbn":"123","status":"Available"}]',
                encoding="utf-8",
            )
            users_file.write_text(
                '[{"id":"005","name":"Member","email":"member@example.com",'
                '"role":"member","borrowed_books":[]}]',
                encoding="utf-8",
            )
            requests_file.write_text('{"requests":[]}', encoding="utf-8")

            library = Library()
            library.load_database(books_file, users_file, requests_file)
            original_books = library.catalog
            original_users = library.users
            original_requests = library.requests
            requests_file.write_text("not valid JSON", encoding="utf-8")

            with self.assertRaises(LibraryDataError):
                library.load_database()

            self.assertIs(library.catalog, original_books)
            self.assertIs(library.users, original_users)
            self.assertIs(library.requests, original_requests)
            self.assertEqual(library.catalog[0].title, "Example")

    def test_legacy_approved_request_uses_book_return_date(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            books_file = root / "books.json"
            users_file = root / "users.json"
            requests_file = root / "requests.json"
            books_file.write_text(
                '[{"book_id":"001","title":"Example","author":"Author",'
                '"isbn":"123","status":"Available",'
                '"borrowed_at":"2026-10-04T10:00:00",'
                '"returned_at":"2026-10-04T11:00:00"}]',
                encoding="utf-8",
            )
            users_file.write_text(
                '[{"id":"005","name":"Member","email":"member@example.com",'
                '"role":"member","borrowed_books":[]}]',
                encoding="utf-8",
            )
            requests_file.write_text(
                '{"requests":[{"user_id":"005","book_id":"001",'
                '"status":"approved","requested_at":"2026-10-04T09:00:00"}]}',
                encoding="utf-8",
            )

            library = Library()
            library.load_database(books_file, users_file, requests_file)

            request = library.requests[0]
            self.assertEqual(request.status, "returned")
            self.assertEqual(request.approved_at, "2026-10-04T10:00:00")
            self.assertEqual(request.returned_at, "2026-10-04T11:00:00")

    def test_legacy_active_loan_without_request_gets_history_record(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            books_file = root / "books.json"
            users_file = root / "users.json"
            requests_file = root / "requests.json"
            books_file.write_text(
                '[{"book_id":"001","title":"Example","author":"Author",'
                '"isbn":"123","status":"Borrowed",'
                '"borrowed_at":"2026-10-04T10:00:00"}]',
                encoding="utf-8",
            )
            users_file.write_text(
                '[{"id":"005","name":"Member","email":"member@example.com",'
                '"role":"member","borrowed_books":[{"book_id":"001",'
                '"date_borrowed":"2026-10-04T10:00:00"}]}]',
                encoding="utf-8",
            )
            requests_file.write_text('{"requests":[]}', encoding="utf-8")

            library = Library()
            library.load_database(books_file, users_file, requests_file)

            self.assertEqual(len(library.requests), 1)
            self.assertEqual(library.requests[0].status, "approved")
            self.assertEqual(library.requests[0].user_id, "005")
            self.assertEqual(library.requests[0].book_id, "001")
            self.assertEqual(library.requests[0].approved_at, "2026-10-04T10:00:00")


if __name__ == "__main__":
    unittest.main()