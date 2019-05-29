import os
import sys
import time
import logging
import config
import argparse
import time
import threading
from BaseAction import BaseAction
from EventHandler import EventHandler
from watchdog.observers.polling import PollingObserver as Observer
import shutil


# returns file size in KB or MB depending on file size
# if file size is less than 900KB output size in KB; MB otherwise
def get_size_auto(file: str):
    size = os.path.getsize(file) / (1 << 10)
    if size < 900:
        return f'{size:6.2f}KB'
    size = size / (1 << 10)
    return f'{size:6.2f}MB'

# copy a source file to a destination
# destination must represent a file
def copyfile(src: str, dest: str):
    if os.path.isdir(dest):
        return
    with open(src, 'rb') as fin:
        with open(f'{dest}\\{filename}', 'wb') as fout:
            shutil.copyfileobj(fin, fout, 128*1024)


class CopyAction(BaseAction):
    def __init__(self, dest: str):
        if not (os.path.exists(dest) and os.path.isdir(dest)):
            logging.error(f"[CopyAction] Passed argument ({dest}) is not a directory.")
            exit(1)
        self.destination = dest
        logging.info(f"[ACTION] Matched files will be copied to {self.destination}")

    def copy_file(self, fullpath, event_type):
        dirname, filename = os.path.split(fullpath)
        # quiet time
        time.sleep(1)
        logging.info(
            f"Copy: <watch_path>\\{filename} to {self.destination}...")
        t1 = time.time()
        copyfile(fullpath, f'{self.destination}\\{filename}')
        t2 = time.time()
        time_total = t2 - t1

        size_auto = get_size_auto(fullpath)
        logging.info(
            f"Done: <watch_path>\\{filename:40s} [{size_auto}] in {time_total:.3f}ms")


    def invoke(self, fullpath: str, event_type: str, is_directory: bool=False):
        if not is_directory:
            t = threading.Thread(target=self.copy_file, args=(fullpath, event_type))
            t.start()
            logging.debug(f"Thread (tid:{t.ident}) created")

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
