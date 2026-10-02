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

    next_id = len(users)+1
    clear_terminal()
    if role == "1":
        print("Creating Member Account\n")
        name = prompt_input("Name")
        email = prompt_input("Email", isEmail=True)
        _, mes = library.register_user("member", next_id, name, email)
        print(mes)

    elif role == "2":
        print("Creating Librarian Account\n")
        name = prompt_input("Name")
        email = prompt_input("Email", isEmail=True)
        department = prompt_input("Department")
        _, mes = library.register_user("librarian", next_id, name, email, department)
        print(mes)


def login_member(users):
    clear_terminal()
    print("Provide information below to login as a member")
    email = prompt_input("Email", isEmail=True)

    if not users:
        print("There are no users")
        return

    data = {}

    for user in users:
      user = user.to_dict()
      if user["email"] == email:
        data = user
      continue

    if data == {}:
        print("User not found")
        return

    prev_page = True
    while prev_page:
        clear_terminal()
        print(f"Welcome back, {data["name"]}\n")
        actions = ["View Profile", "Request Book"]

        for idx, action in enumerate(actions, 1):
          print(f"[{idx}] {action}")

        user_action = input("\nPick an action: ").strip()

        while user_action not in ["1", "2"]:
          print("Action invalid")
          user_action = input("\nPick an action: ").strip()

        clear_terminal()
        if user_action == "1":
            print("Viewing Profile\n")
            print(f"Name: {data["name"]}" \
            f"Email: {data["email"]}" 
            )
            if not data["borrowed_books"]:
                print("No borrowed books")
                return
            for b in data["borrowed_books"]:
                print(b)
            print()

        elif user_action == "2":
            print("Request a book")

        prev = input("Anything else y/N: ")
        if prev == "y":
            prev_page = True
        else:
            prev_page = False

    clear_terminal()