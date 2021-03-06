import os
import re
import time
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from actions import BaseAction
import logging
from config import ConfigObject


# TODO: implement quiet period for events based on file name
class FileEvent:
    def __init__(self, filename: str, time_to_run: float):
        self.filename = filename
        self.time_to_run = time_to_run

    @property
    def can_run(self) -> bool:
        return time.time >= self.time_to_run


class EventHandler(FileSystemEventHandler):
    file_queue = []
    def __init__(self, config_object: ConfigObject):
        self.include_list = config_object.include_list
        self.exclude_list = config_object.exclude_list
        self.action = BaseAction

    def file_is_included(self, filename) -> bool:
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

    def handle_file(self, event: FileSystemEvent):
        fullpath = os.path.abspath(event.src_path)
        dirname, filename = os.path.split(fullpath)
        if self.file_is_included(filename):
            self.action.invoke(fullpath, event.event_type, is_directory=event.is_directory)

    def on_modified(self, event: FileSystemEvent):
        self.handle_file(event)

    def on_created(self, event: FileSystemEvent):
        self.handle_file(event)
