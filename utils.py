def clear_terminal():
    import sys
    sys.stdout.write("\033[H\033[2J\033[3J")
    sys.stdout.flush()

def get_user_role():
    print("Welcome to console LMS")
    print("Choose your current position\n")

    for idx, role in enumerate(["Create Account", "Login (Member)", "Login (Librarian)"], 1):
        print(f"[{idx}] {role}")

    user_action = input("\nChoose a role: ").strip()

    while user_action not in ["1", "2", "3"]:
        print(f"{user_action} is an invalid role.\nTry [1] Librarian or [2] Member")
        user_action = input("Choose a role: ").strip()

    return user_action

def is_valid_syntax(email_input):
    import re
    EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if re.fullmatch(EMAIL_REGEX, email_input):
        return True
    return False

def prompt_input(label, isEmail=False):
    value = input(f"{label}: ").strip()
    
    if isEmail:
        while is_valid_syntax(value) == False:
            print("\n!!! Enter Valid Email")
            value = input(f"{label}: ").strip()
            is_valid_syntax(value)

    else:
        while not value:
            print(f"\n!!! {label} cannot be empty. Please try again.")
            value = input(f"{label}: ").strip()

    return value


def create_account(library, users):
    print("Create Account Page\n")

    print("Available Account Type")
    account_roles = ["Member", "Librarian"]

    for idx, role in enumerate(account_roles, 1):
        print(f"[{idx}] {role}")

    role = input("\nChoose an account type 1[Member] 2[Librarian]: ").strip()

    while role not in ["1", "2"]:
        print("Invalid Actions")
        role = input("Choose an account type 1[Member] 2[Librarian]: ").strip()

    users_dict = [user.to_dict() for user in users]
    if users_dict:
        last_user_id = max(int(user["id"]) for user in users_dict)
        next_id = f"{last_user_id + 1:03d}"
    else:
        next_id = "001"

    clear_terminal()
    if role == "1":
        print("Creating Member Account\n")
        _, mes = library.register_user(
            "member", 
            next_id, 
            prompt_input("Name"), 
            prompt_input("Email", isEmail=True)
        )
        print(mes)

    elif role == "2":
        print("Creating Librarian Account\n")
        _, mes = library.register_user(
            "librarian", 
            next_id, 
            prompt_input("Name"), 
            prompt_input("Email", isEmail=True), 
            prompt_input("Department")
        )
        print(mes)

from models import Member
def login_member(users, books, library):
    clear_terminal()
    print("Provide your registered email to login as a member\n")
    email = prompt_input("Email", isEmail=True)

    if not users:
        print("There are no users")
        return

    data = {}

    for user in users:
        user = user.to_dict()
        if user["email"] == email:
            data = user
            break

    if data == {}:
        print("User not found")
        return

    while True:
        clear_terminal()
        print(f"Welcome back, {data['name']}\n")
        actions = ["View Profile", "Request Book", "View Book Status", "Return Books", "Logout"]
        
        for idx, action in enumerate(actions, 1):
            print(f"[{idx}] {action}")
    
        user_action = input("\nPick an action: ").strip()

        if user_action not in ["1", "2", "3", "4", "5"]:
            print("Action invalid")
            input("Press Enter to continue...")
            continue

        clear_terminal()

        if user_action == "1":
            print("Profile Details\n")

            print(f"Name: {data["name"]}")
            print(f"Email: {data["email"]}") 

            if not data["borrowed_books"]:
                print(f"Borrowed Books: {len(data["borrowed_books"])}\n")
            else:
                print(f"\n{"Book ID":<10} {"Title":<30} {"Author":<20} {"ISBN":<15} {"Status":<10}")
                for b in data["borrowed_books"]:
                    print(f"{b["book_id"]:<10} {b["title"]:<30} {b["author"]:<20} {b["isbn"]:<15} {b["status"]:<10}")

            print()

        elif user_action == "2":
            print("Request a book")

            if not books:
                print("No books available")
                return

            print(f"\n{"Book ID":<10} {"Title":<30} {"Author":<20} {"ISBN":<15} {"Status":<10}")
            for book in books:
                book = book.to_dict()
                print(f"{book["book_id"]:<10} {book["title"]:<30} {book["author"]:<20} {book["isbn"]:<15} {book["status"]:<10}")

            book_id = prompt_input("\nEnter Book ID to request: ").strip()

            all_books_ids = [book.to_dict()["book_id"] for book in books]
            available_books_ids = [book.to_dict()["book_id"] for book in books if book.to_dict()["status"] == "Available"]
            
            while book_id not in all_books_ids:
                print("Book ID doesn't exist")
                book_id = prompt_input("\nEnter Book ID to request: ").strip()
                

            while book_id not in available_books_ids:
                print("this book isn't available currently")
                book_id = prompt_input("\nEnter another Book ID to request: ").strip()

            member = Member(
                data["id"], 
                data["name"], 
                data["email"]
            )

            book_to_request = next((book for book in books if book.to_dict()["book_id"] == book_id), None)

            _, mes = member.request_book(library, book_to_request)
            print(mes)



        elif user_action == "3":
            print("Viewing My Books Status\n")

        elif user_action == "4":
            print("Return Book")

        elif user_action == "5":
            print("Logging out...")
            break

        prev = input("Anything else y/N: ").strip().lower()
        if prev != "y":
            break



from models import Librarian
def login_librarian(users, books, library):
    clear_terminal()
    print("Provide registered email to login as a librarian")

    email = prompt_input("Email", isEmail=True)

    if not users:
        print("There are no users")
        return

    data = {}

    for user in users:
        user = user.to_dict()
        if user["email"] == email:
            if user["role"] == "librarian":
                data = user
            else:
                print(f"{email} is not a librarian")
            break


    if data == {}:
        print("User not found")
        return

    while True:
        clear_terminal()
        print(f"Welcome back, {data['name']}\n")
        actions = ["View Profile", "Add Book", "Approve Book Request", "View All Books", "Logout"]
        
        for idx, action in enumerate(actions, 1):
            print(f"[{idx}] {action}")
    
        user_action = input("\nPick an action: ").strip()

        if user_action not in ["1", "2", "3", "4", "5"]:
            print("Action invalid")
            input("Press Enter to continue...")
            continue

        clear_terminal()

        if user_action == "1":
            print("Profile Details\n")

            print(f"Name: {data["name"]}")
            print(f"Email: {data["email"]}") 
            print(f"Department: {data["department"]}")

        elif user_action == "2":
            print("Adding a book")
            librarian = Librarian(
                data["id"], 
                data["name"], 
                data["email"], 
                data["department"]
            )

            books_dict = [book.to_dict() for book in books]
            if books_dict:
                last_book_id = max(int(book["book_id"]) for book in books_dict)
                next_book_id = f"{last_book_id + 1:03d}"
            else:
                next_book_id = "001"
            
            _, msg = librarian.add_book(
                library,
                next_book_id,
                prompt_input("Book Title"),
                prompt_input("Book Author"),
                prompt_input("Book ISBN")
            )

            print(msg)


        elif user_action == "3":
            print("Approving Book Request")

        elif user_action == "4":
            print("Viewing All Books\n")

        elif user_action == "5":
            print("Logging out...")
            break

        prev = input("Anything else y/N: ").strip().lower()
        if prev != "y":
            break

