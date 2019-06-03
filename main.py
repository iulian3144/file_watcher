import os
import sys
import time
import logging
import config
import argparse
import time
import threading
from actions import CopyAction
from actions import BaseAction
from EventHandler import EventHandler
from watchdog.observers.polling import PollingObserver as Observer
import shutil


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

    watcher_config = config.WatcherConfig()
    config_object = watcher_config.config_object
    args = parser.parse_args()

    action_name = args.action or config_object.action
    action_arg = args.action_arg or config_object.action_arg
    watch_path = args.watch_path or config_object.watch_path

    while True:
        if action_name not in ACTION_LIST:
            logging.error(f"Action '{args.action}' is not a valid action name!")
            exit(1)
        action = ACTION_LIST[action_name]
        logging.info(f'watch path: {watch_path}; action({action}): {action_name}({action_arg})')

        event_handler = EventHandler(config_object)
        event_handler.action = action(action_arg)
        observer = Observer(timeout=1)
        observer.schedule(event_handler, watch_path, recursive=False)
        observer.start()

        if watcher_config.watch_configuration() == config.CONFIG_CHANGED:
            action_name = config_object.action
            action_arg = config_object.action_arg
            watch_path = config_object.watch_path
            logging.debug("Stopping observer...")
            observer.stop()
            logging.debug("Waiting for observer...")
            observer.join()
            continue
        break
    logging.info("Quitting...")
    observer.stop()
    observer.join()
