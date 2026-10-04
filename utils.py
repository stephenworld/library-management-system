import re
import sys

from models import Library, LibraryError, Librarian, Member


def clear_terminal():
    sys.stdout.write("\033[H\033[2J\033[3J")
    sys.stdout.flush()


def get_user_role():
    print("Welcome to console LMS")
    print("Choose your current position\n")
    actions = ["Create Account", "Login (Member)", "Login (Librarian)"]
    for index, action in enumerate(actions, 1):
        print(f"[{index}] {action}")

    choice = input("\nChoose a role: ").strip()
    while choice not in {"1", "2", "3"}:
        print(f"{choice} is an invalid role. Choose 1, 2, or 3.")
        choice = input("Choose a role: ").strip()
    return choice


def prompt_input(label, is_email=False):
    value = input(f"{label}: ").strip()
    email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    while not value or (is_email and not re.fullmatch(email_pattern, value)):
        print("Enter a valid email address." if is_email else f"{label} cannot be empty.")
        value = input(f"{label}: ").strip()
    return value


def create_account(library, users):
    print("Create Account Page\n")
    print("[1] Member\n[2] Librarian\n")
    role_choice = input("Choose an account type: ").strip()

    while role_choice not in {"1", "2"}:
        print("\n!!! Invalid account type.")
        role_choice = input("Choose [1] Member or [2] Librarian: ").strip()

    clear_terminal()
    next_id = _next_id(users, "id")
    role = "member" if role_choice == "1" else "librarian"
    print("\nCreate your account")
    name = prompt_input("Name")
    email = prompt_input("Email", is_email=True)
    department = prompt_input("Department") if role == "librarian" else None
    _, message = library.register_user(role, next_id, name, email, department)
    print(message)


def login_member(users, books, library):
    email = prompt_input("Registered member email", is_email=True).casefold()
    matching_member = next(
        (
            user for user in users
            if isinstance(user, Member) and user.email.casefold() == email
        ),
        None,
    )
    if matching_member is None:
        print("Member not found.")
        return
    member = matching_member

    while True:
        clear_terminal()
        print(f"Welcome back, {member.name}\n")
        actions = ["View Profile", "Request Book", "View Book Status", "Return Book", "Sync Data", "Logout"]
        for index, action in enumerate(actions, 1):
            print(f"[{index}] {action}")
        choice = input("\nPick an action: ").strip()

        clear_terminal()

        try:
            if choice == "1":
                _show_member_profile(member)
            elif choice == "2":
                _request_book(member, books, library)
            elif choice == "3":
                _show_member_status(member, library)
            elif choice == "4":
                _return_book(member, library)
            elif choice == "5":
                member_id = member.id
                sync_data(library, books, users)
                matching_member = next(
                    (
                        user for user in users
                        if isinstance(user, Member) and user.id == member_id
                    ),
                    None,
                )
                if matching_member is None:
                    print("Your account no longer exists; you have been logged out.")
                    return
                member = matching_member
            elif choice == "6":
                print("Logging out...")
                return
            else:
                print("Action invalid.")
        except LibraryError as error:
            print(error)
        input("\nPress Enter to continue...")


def login_librarian(users, books, library):
    clear_terminal()
    email = prompt_input("Registered librarian email", is_email=True).casefold()
    matching_librarian = next(
        (
            user for user in users
            if isinstance(user, Librarian) and user.email.casefold() == email
        ),
        None,
    )
    if matching_librarian is None:
        print("Librarian not found.")
        return
    librarian = matching_librarian

    while True:
        clear_terminal()
        print(f"Welcome back, {librarian.name}\n")

        actions = ["View Profile", "Add Book", "Approve Book Request", "View All Books", "Sync Data", "Logout"]
        for index, action in enumerate(actions, 1):
            print(f"[{index}] {action}")
        choice = input("\nPick an action: ").strip()
        clear_terminal()

        try:
            if choice == "1":
                print("Librarian Profile\n")

                print(f"Name: {librarian.name}\nEmail: {librarian.email}")
                print(f"Department: {librarian.department}")
            elif choice == "2":
                print("Record New Book\n")

                book, message = librarian.add_book(
                    library,
                    _next_id(books, "book_id"),
                    prompt_input("Book Title"),
                    prompt_input("Book Author"),
                    prompt_input("Book ISBN"),
                )
                print(message)
            elif choice == "3":
                print("Review Requests\n")

                _review_requests(librarian, library)
            elif choice == "4":
                _show_books(books)
            elif choice == "5":
                librarian_id = librarian.id
                sync_data(library, books, users)
                matching_librarian = next(
                    (
                        user for user in users
                        if isinstance(user, Librarian) and user.id == librarian_id
                    ),
                    None,
                )
                if matching_librarian is None:
                    print("Your account no longer exists; you have been logged out.")
                    return
                librarian = matching_librarian
            elif choice == "6":
                print("Logging out...")
                return
            else:
                print("Action invalid.")
        except LibraryError as error:
            print(error)
        input("\nPress Enter to continue...")


def _request_book(member, books, library):
    print("Request a book")
    _show_books(books)
    book_id = prompt_input("\nEnter Book ID to request")
    book = next((item for item in books if item.book_id == book_id), None)
    if book is None:
        print("Book ID does not exist.")
        return
    _, message = member.request_book(library, book)
    print(message)


def _show_member_profile(member):
    print("Member Profile")
    print(f"\nName: {member.name}\nEmail: {member.email}")
    print(f"Active borrowed books: {len(member.borrowed_books)}")
    _show_books(member.borrowed_books)


def _show_member_status(member, library):
    print("Your requests")
    member_requests = [
        request for request in library.requests if request.user_id == member.id
    ]
    if not member_requests:
        print("\nNo requests.")

    for request in member_requests:
        book = next(book for book in library.catalog if book.book_id == request.book_id)
        print(
            f"Request {request.request_id}: {book.title} - {request.status}; "
            f"requested {request.requested_at}"
        )
        if request.approved_at:
            print(f"  Approved: {request.approved_at}")
        if request.returned_at:
            print(f"  Returned: {request.returned_at}")

    print("\nYour borrowed books")
    _show_books(member.borrowed_books)


def _return_book(member, library):
    if not member.borrowed_books:
        print("You have no books to return.")
        return
    _show_books(member.borrowed_books)
    book_id = prompt_input("Enter Book ID to return")
    _, message = library.return_book(member.id, book_id)
    print(message)


def _review_requests(librarian, library):
    requests = library.list_pending_requests()
    if not requests:
        print("There are no pending requests.")
        return
    print("\nPending requests")
    for request in requests:
        member = next(user for user in library.users if user.id == request.user_id)
        book = next(book for book in library.catalog if book.book_id == request.book_id)
        print(
            f"[{request.request_id}] {member.name} requests "
            f"[{book.book_id}] {book.title}"
        )
    try:
        request_id = int(prompt_input("Request ID"))
    except ValueError:
        print("Request ID must be a number.")
        return
    decision = input("Approve or reject [a/r]: ").strip().lower()
    if decision == "a":
        _, message = library.approve_request(request_id)
    elif decision == "r":
        _, message = library.reject_request(request_id)
    else:
        print("No change made.")
        return
    print(f"Librarian {librarian.name}: {message}")


def _show_books(books):
    if not books:
        print("\nNo books to display.")
        return

    print("-"*100)
    print(f"{'Book ID':<10} | {'Title':<30} | {'Author':<24} | {'ISBN':<16} | {'Status':<10}")
    print("-"*100)

    for book in books:
        print(f"{book.book_id:<10} | {book.title:<30} | {book.author:<24} | {book.isbn:<16} | {book.status}")
    print("-"*100)


def sync_data(library, books, users):
    refreshed_books, refreshed_users, message = library.load_database()
    books[:] = refreshed_books
    users[:] = refreshed_users
    library.catalog = books
    library.users = users
    print(message)


def _next_id(records, attribute):
    values = [int(getattr(record, attribute)) for record in records]
    return f"{max(values, default=0) + 1:03d}"