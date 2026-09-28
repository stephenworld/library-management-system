from utils.helper import prompt_input
from utils.update_books import generate_book_id, update_book

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
    "history": [
      {}
    ]
  }

  update_book(book_details)
