from utils import get_user_role, clear_terminal, create_account, login_member, login_librarian
from models import Library


library = Library()
books, users, message = library.load_database()

exit = "y"
while exit == "y":
  clear_terminal()

  action = get_user_role()
  match action:
    case "1":
      create_account(library, users)
    case "2":
      login_member(users)
    case "3":
      login_librarian(users)
    case _:
      print("Unknown Action")

  exit = input("Do you want to perform any other action y/N: ").strip().lower()

  clear_terminal()
  while exit != "y":
    print("Program exitted!!!")
    break


