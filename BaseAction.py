import logging

class BaseAction:
    def __init__(self, arg):
        pass
    def invoke(self, fullpath, event_type, is_directory=False):
        logging.info(f'[{event_type}] File path: {fullpath}')
