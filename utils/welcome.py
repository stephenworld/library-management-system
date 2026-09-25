features = ["Add books", "Remove books", "Search for books", "Register members", "Borrow Books", "Return Books", "View Available Books", "View Borrowed books"]
def welcome():
  print("Managing a Small Library\n")
  for idx, feature in enumerate(features, 1):
    print(f"[{idx}] {feature}")