from models import Library, LibraryDataError
from utils import clear_terminal, create_account, get_user_role, login_librarian, login_member

clear_terminal()
def main() -> None:
    library = Library()
    try:
        books, users, message = library.load_database()
    except LibraryDataError as error:
        print(f"Unable to load library data: {error}")
        return

    print(message)
    print()
    while True:
        action = get_user_role()
        clear_terminal()
        try:
            if action == "1":
                create_account(library, users)
            elif action == "2":
                login_member(users, books, library)
            elif action == "3":
                login_librarian(users, books, library)
        except LibraryDataError as error:
            print(f"Could not save library data: {error}")

        again = input("Do you want to perform another action? y/N: ").strip().lower()
        if again != "y":
            print("Program exited.")
            return
        clear_terminal()


if __name__ == "__main__":
    main()


