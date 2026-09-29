from utils.helper import clear_terminal
from utils.config import add_book, remove_book

roles = ["Librarian", "Member"]

librarian_actions = ["Add books", "Remove books","View Members", "View Available Books", "View Borrowed books"]
member_actions = ["Borrow Books", "Return Books", "View Available Books"]

def user_role():
  clear_terminal()
  print("Welcome to console LMS")
  print("Choose your current position\n")

  for idx, role in enumerate(roles, 1):
    print(f"[{idx}] {role}")

  user_action = input("\nChoose a role: ").strip()

  while user_action not in ["1", "2"]:
    print(f"{user_action} is an invalid role.\nTry [1] Librarian or [2] Member")
    user_action = input("Choose a role: ").strip()

  return user_action

def librarian_features():
  clear_terminal()
  print("Logged in as a Librarian\n")
  print("Below are the available actions\n")

  for idx, action in enumerate(librarian_actions, 1):
    print(f"[{idx}] {action}")

  user_action = input("\nSelect an action: ").strip()

  while user_action not in ["1", "2", "3", "4", "5"]:
    "View Members", "View Available Books", "View Borrowed books"
    print(f"{user_action} is an invalid action.\nTry [1] Add Books, [2] Remove Books, [3] View Members, [4] View Available Books or [5] View Borrowed books")
    user_action = input("Select an action: ").strip()

  if user_action == "1":
    clear_terminal()
    add_book()

  elif user_action == "2":
    clear_terminal()
    remove_book()

  elif user_action == "3":
    """
    View Members
    """
  elif user_action == "4":
    """
    View Available Books
    """
  elif user_action == "5":
    """
    View Borrowed books
    """



def member_features():
  clear_terminal()
  print("Logged in as a Member")
  print("Below are the available actions\n")

  for idx, action in enumerate(member_actions, 1):
    print(f"[{idx}] {action}")

  user_action = input("\nSelect an action: ").strip()

  while user_action not in ["1", "2", "3"]:
    print(f"{user_action} is an invalid action.\nTry [1] Borrow Books, [2] Return Books or [3] View Available Books")
    user_action = input("Select an action: ").strip()

  if user_action == "1":
    """
    Borrow Books
    """
  elif user_action == "2":
    """
    Return Books
    """
  elif user_action == "3":
    """
    View Available Books
    """
