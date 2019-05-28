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
parser.add_argument('--path', metavar='PATH', dest='path', default='.',
                    help='path to watch for file changes', )
parser.add_argument('--action', metavar='ACTION', dest='action', default='default',
                    help='action name:\n\
  copy - copy files to DESTINATION\n\
  default - echo file name')
parser.add_argument('--destination', metavar='DESTINATION', dest='destination', default='.',
                    help='where to copy the watched files')

if __name__ == "__main__":
    FORMAT = "[%(asctime)s][%(levelname)s] %(message)s"
    DATEFMT = "%d-%m-%Y %H:%M:%S"
    logging.basicConfig(format=FORMAT, datefmt=DATEFMT, level=logging.INFO)

    args = parser.parse_args()
    watch_path = args.path
    destination = args.destination
    logging.info(f'watch path: {watch_path}')

    config_object = config.initialize()

    event_handler = EventHandler(config_object)
    event_handler.action = ACTION_LIST[args.action](destination)
    observer = Observer()
    observer.schedule(event_handler, watch_path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
