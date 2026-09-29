json_file = "data/data.json"
import json

def fetch_data():
  try:
    with open(json_file, "r") as file:
      data = json.load(file)
  except FileNotFoundError:
    data = {}

  return data

def generate_book_id():
  import re
  data = fetch_data()
  books =  data["books"]
  max_num = 0
  prefix = "book_"

  pattern = re.compile(rf"^{re.escape(prefix)}(\d+)$")

  if len(books) == 0:
    max_num = 0
  else:
    for book in books:
      book_id = book["id"]
      match = pattern.match(book_id)
      if match:
        num = int(match.group(1))
        if num > max_num:
          max_num = num

  next_num = max_num + 1

  return f"{prefix}{next_num:03d}"

def update_book(entry):
  data = fetch_data()
  books = list(data["books"])
  books.append(entry)
  data["books"] = books

  with open(json_file, "w") as file:
    json.dump(data, file, indent=2)

def delete_book(book_id):
  data = fetch_data()
  books = list(data["books"])
  
  updated_books = [book for book in books if book["id"] != book_id]

  data["books"] = updated_books
  with open(json_file, "w") as file:
    json.dump(data, file, indent=2)

def get_book_detail(book_id):
  data = fetch_data()
  books = data.get("books", [])

  return next((book for book in books if book["id"] == book_id), None)
