def clear_terminal():
  import sys
  sys.stdout.write("\033[H\033[2J\033[3J")
  sys.stdout.flush()

def prompt_input(label):
  value = input(f"{label}: ").strip()
  
  while not value:
    print(f"\n!!! {label} cannot be empty. Please try again.")
    value = input(f"{label}: ").strip()

  return value