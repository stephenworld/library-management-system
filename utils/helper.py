def clear_terminal():
  import sys
  sys.stdout.write("\033[H\033[2J\033[3J")
  sys.stdout.flush()