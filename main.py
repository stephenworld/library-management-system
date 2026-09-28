from action import user_role, librarian_features, member_features

role = user_role()

if role == "1":
  librarian_features()
elif role == "2":
  member_features()

