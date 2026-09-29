from utils.helper import prompt_input
from utils.update_books import generate_book_id, update_book, fetch_data, delete_book, get_book_detail

def add_book():
  print("ADD NEW BOOK TO CATALOG")
  print("Fill in the book details below.\n")

  title = prompt_input("Title")
  author = prompt_input("Author")
  isbn = prompt_input("ISBN")
  book_id = generate_book_id()

  book_details = {
    "id": book_id,
    "title": title,
    "author": author,
    "ISBN": isbn,
    "available": True,
    "history": []
  }

  update_book(book_details)

def remove_book():
  print("REMOVE BOOK FROM CATALOG")
  data = fetch_data()
  books = data["books"]
  
  if not books:
    print("There is no book in the library")
    return

  for idx, book in enumerate(books, 1):
    book_id = book["id"]
    title = book["title"]
    author = book["author"]
    isbn = book["ISBN"]
    available = book["available"]
    history = book["history"]
    
    print()
    print(f"--- Book {idx}: {title} ---")
    print(f"Author:    {author}")
    print(f"ID/ISBN:   {book_id} / {isbn}")
    print(f"Available: {available}")
    if history:
      print("\nHistory")
      for idx, his in enumerate(history, 1):
        member_id = his["member_id"]
        borrowed_date = his["borrowed_date"]
        returned_date = his["returned_date"]
        print(f"{idx} {member_id} lend the book on {borrowed_date} and returned {returned_date}")
    else:
      print("\nHistory:   No checkout history")

  id_to_delete = input("Select the book ID you want to delete: ").strip().lower()
  while id_to_delete == "":
    print("book ID can't be blank")
    id_to_delete = input("Enter a valid book ID: ").strip()

  while id_to_delete not in [book_id for book["book_id"] in books]:
    print("Invalid book ID.")
    id_to_delete = input("Enter a valid book ID: ").strip()


  delete_book(id_to_delete)
  print("Book has been removed from the Library")

def view_members():
  print("VIEW ALL MEMBERS")
  data = fetch_data()
  members = data["members"]

  if not members:
    print("No Registered member")

  for member in members:
    name = member["name"]
    id = member["member_id"]
    borrowed_books = member["borrowed_books"]

    print()
    print("--- Member Details ---")
    print(f"Name:       {name}")
    print(f"Member ID:  {id}")

    print("-" * 70)
    print(f"{"Book ID":<10} | {"Title":<20} | {"Author":<20} | {"Status"}")
    print("-" * 70)

    if borrowed_books:
      for borrowed_book in borrowed_books:
        book_id = borrowed_book["id"]
        details = get_book_detail(book_id)
        status = borrowed_book["status"]

        print(f"{book_id:<10} | {details["title"]:<20} | {details["author"]:<20} | {status}")
    else:
      print(f"{name} hasn't read any book from the library")

def view_books(status, message):
  print("SHOWING AVILABLE BOOKS IN LIBRARY")
  data = fetch_data()
  books = data["books"]

  if not books:
    print("There is no book in the library")
    return

  available_books = [book for book in books if book["available"] == status]

  if not available_books:
    print(message)

  for idx, book in enumerate(available_books, 1):
    book_id = book["id"]
    title = book["title"]
    author = book["author"]
    isbn = book["ISBN"]
    available = book["available"]
    history = book["history"]
    
    print()
    print(f"--- Book {idx}: {title} ---")
    print(f"Author:    {author}")
    print(f"ID/ISBN:   {book_id} / {isbn}")
    print(f"Available: {available}")
    if history:
      print("\nHistory")
      for idx, his in enumerate(history, 1):
        member_id = his["member_id"]
        borrowed_date = his["borrowed_date"]
        returned_date = his["returned_date"]
        print(f"{idx} {member_id} lend the book on {borrowed_date} and returned {returned_date}")
    else:
      print("\nHistory:   No checkout history")
