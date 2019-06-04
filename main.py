import os
import logging
import config
import argparse
from actions import CopyAction
from actions import BaseAction
from EventHandler import EventHandler
from watchdog.observers.polling import PollingObserver as Observer


ACTION_LIST = {
    'default': {
        "class": BaseAction,
        "description": "echoes file path"},
    'copy': {
        "class": CopyAction,
        "description": "copy files to the directory specified by <action_arg>"}
}

parser = argparse.ArgumentParser(
    description='File Watcher', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--watch_path', metavar='PATH', dest='watch_path',
                    help='path to watch for file changes', )
parser.add_argument('--action', dest='action', choices=ACTION_LIST.keys(),
                    help='action name')
parser.add_argument('--action_arg', metavar='ACTION_ARG', dest='action_arg',
                    help='action argument')
parser.add_argument('--list_actions', dest="list_actions", action="store_true",
                    help='list actions')


def list_actions():
    for action_name, definition in ACTION_LIST.items():
        print(f"{action_name:>10s} : {definition['description']}")


LOG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'file_watcher.log')
if __name__ == "__main__":
    FORMAT = "[%(asctime)s][%(levelname)s] %(message)s"
    DATEFMT = "%d-%m-%Y %H:%M:%S"
    logging.basicConfig(format=FORMAT, level=logging.INFO)

    watcher_config = config.WatcherConfig()
    config_object = watcher_config.config_object
    args = parser.parse_args()

    if args.list_actions:
        list_actions()
        exit()

    action_name = args.action or config_object.action
    action_arg = args.action_arg or config_object.action_arg
    watch_path = args.watch_path or config_object.watch_path

    while True:
        action = ACTION_LIST[action_name]['class']
        logging.info(f'watch path: {watch_path}; action: {action_name}({action_arg})')

        event_handler = EventHandler(config_object)
        event_handler.action = action(action_arg)
        observer = Observer(timeout=0.5)
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
