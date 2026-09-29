from utils.helper import prompt_input
from utils.update_books import generate_book_id, update_book, fetch_data, delete_book

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
    print("Book is empty")

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

