
VERBOSE = False

def set_verbose(v):
  global VERBOSE
  VERBOSE = v

def log(msg):
  print(msg)

def log_verbose(msg):
  global VERBOSE
  if VERBOSE:
    log(msg)