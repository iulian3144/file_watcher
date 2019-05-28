class BaseAction:
    def __init__(self, arg):
        pass
    def invoke(self, fullpath, event_type, is_directory=False):
        print(f'[{fullpath}] Full file path: {event_type}')
