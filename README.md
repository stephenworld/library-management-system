# Library Management System

A Python console application for managing a small library.

## Features

- Members can view books, request available books, check request and borrowing
  status, and return borrowed books.
- Librarians can add books and approve or reject member requests.
- Each checkout is recorded separately in the request history, including
  request, approval, and return timestamps.
- Members and librarians can sync their menus with the JSON data files.

## Data Files

- `database/books.json` stores the book catalog and current availability.
- `database/users.json` stores member and librarian accounts and active loans.
- `database/requests.json` stores request decisions and checkout history.

## Run

From the project directory:

```bash
python3 main.py
```

Run the tests with:

```bash
python3 -m unittest discover -s tests -v
```
