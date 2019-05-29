import logging

class BaseAction:
    def __init__(self, arg):
        pass
    def invoke(self, fullpath: str, event_type: str, is_directory: bool=False):
        item_type = "dir" if is_directory else "file"
        logging.info(f'[{item_type:>4s} {event_type}] path: {fullpath}')
