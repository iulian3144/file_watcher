import os
import re
from watchdog.events import FileSystemEventHandler
from BaseAction import BaseAction
import logging


class EventHandler(FileSystemEventHandler):
    def __init__(self, config_object):
        self.include_list = config_object.include_list
        self.exclude_list = config_object.exclude_list
        self.action = BaseAction

    def file_is_included(self, filename):
        include = False
        for item in self.include_list:
            logging.debug(
                f"Checking '{filename}' against regex '{item}'...")
            if(re.match(item, filename)):
                include = True
        for item in self.exclude_list:
            logging.debug(
                f"Checking '{filename}' against regex '{item}'...")
            if(re.match(item, filename)):
                include = False
        incl_string = "included" if include else "excluded"
        logging.debug(f"File '{filename}' will be {incl_string}")
        return include

    def handle_file(self, event):
        fullpath = os.path.abspath(event.src_path)
        dirname, filename = os.path.split(fullpath)
        if self.file_is_included(filename):
            self.action.invoke(fullpath, event.event_type, is_directory=event.is_directory)

    def on_modified(self, event):
        self.handle_file(event)

    def on_created(self, event):
        self.handle_file(event)
