import argparse

def arguments_parse(epilog_text):
  parser = argparse.ArgumentParser(
      description="Set up and run a single use render farm for Blender on AWS.",
      epilog=epilog_text,
      formatter_class=argparse.RawDescriptionHelpFormatter
    )
  main_group = parser.add_argument_group()
  main_group.add_argument("-p", "--project_file",
    help="the project filename or filepath",
    default="example/project.yaml")
  main_group.add_argument("-v", "--verbose",
      help="switch on verbose output.",
      action= "store_true"
    )
  project_actions_group = parser.add_mutually_exclusive_group()
  project_actions_group.add_argument("-s", "--stop",
      help="stop the EC2 servers and place the farm in a stopped state",
      action="store_true"
    )
  project_actions_group.add_argument("-r", "--run",
      help="run or restart. this first syncs the project files up to the farm and then starts rendering",
      action= "store_true"
    )
  project_actions_group.add_argument("-c", "--create_stack",
      help="create stack, once created you can start rendering with --run. ",
      action= "store_true"
    )
  project_actions_group.add_argument("-k", "--kill",
      help="stop the EC2 servers if running and tear down the stack - INCLUDING THE RENDER OUTPUT BUCKET!",
      action= "store_true"
    )
  project_actions_group.add_argument("-ck", "--create_key_pair",
      help="creates a key pair for ssh access",
      action= "store_true"
    )



  return parser.parse_args()