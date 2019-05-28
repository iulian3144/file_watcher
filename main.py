import os
import sys
import time
import logging
import config
import argparse
from BaseAction import BaseAction
from EventHandler import EventHandler
from watchdog.observers.polling import PollingObserver as Observer
import shutil


class CopyAction(BaseAction):
    def __init__(self, dest):
        if not (os.path.exists(dest) and os.path.isdir(dest)):
            logging.error(f"[CopyAction] Passed argument ({dest}) is not a directory.")
            exit(1)
        self.destination = dest

    def invoke(self, fullpath, event_type, is_directory=False):
        if not is_directory:
            logging.info(f"Copying '{fullpath}' to '{self.destination}'...")
            shutil.copy(fullpath, self.destination)

ACTION_LIST = {
    'default': BaseAction,
    'copy': CopyAction
}

parser = argparse.ArgumentParser(
    description='File Watcher', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--watch_path', metavar='PATH', dest='watch_path',
                    help='path to watch for file changes', )
parser.add_argument('--action', metavar='ACTION', dest='action',
                    help='action name; valid values:\n\
  copy - copy files to ACTION_ARG\n\
  default - echo file name')
parser.add_argument('--action_arg', metavar='ACTION_ARG', dest='action_arg',
                    help='action argument')

if __name__ == "__main__":
    FORMAT = "[%(asctime)s][%(levelname)s] %(message)s"
    DATEFMT = "%d-%m-%Y %H:%M:%S"
    logging.basicConfig(format=FORMAT, datefmt=DATEFMT, level=logging.INFO)

    config_object = config.initialize()
    args = parser.parse_args()

    action_name = args.action or config_object.action
    action_arg = args.action_arg or config_object.action_arg
    watch_path = args.watch_path or config_object.watch_path

    if args.watch_path is not None:
        watch_path = args.watch_path
    if args.action not in ACTION_LIST:
        logging.error(f"Action '{args.action}' is not a valid action name!")
        exit(1)
    action = ACTION_LIST[action_name]
    logging.info(f'watch path: {watch_path}')
    logging.info(f'    action: {action_name} ({action})')
    logging.info(f'action arg: {action_arg}')


    event_handler = EventHandler(config_object)
    event_handler.action = action(action_arg)
    observer = Observer()
    observer.schedule(event_handler, watch_path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
