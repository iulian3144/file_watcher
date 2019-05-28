import os
import sys
import yaml
import logging


__CONFIG_FILE = 'config.yml'

class WatcherConfig():
    def __init__(self, config_object):
        self.watch_path = '.'
        self.action = 'default'
        self.action_arg = ''
        self.__include_list = []
        self.__exclude_list = []
        if config_object:
            self.__include_list = config_object["include"]
            self.__exclude_list = config_object["exclude"]
            if 'watch_path' in config_object:
                self.watch_path = config_object['watch_path']
            if 'action' in config_object:
                self.action = config_object['action']
            if 'action_arg' in config_object:
                self.action_arg = config_object['action_arg']

    @property
    def include_list(self):
        return self.__include_list

    @property
    def exclude_list(self):
        return self.__exclude_list



def initialize():
    config_object = {}
    config_path = os.path.dirname(sys.argv[0])
    config_path = os.path.abspath(config_path)
    config_path = f'{config_path}\\{__CONFIG_FILE}'
    if not os.path.isfile(config_path):
        logging.warn(f"Configuration file '{config_path}' does not exist!")
    else:
        with open(config_path, 'r') as config_file:
            logging.info(f"Loading configuration file {config_path}...")
            config_object = yaml.load(config_file, Loader=yaml.BaseLoader)

    return WatcherConfig(config_object)



if __name__ == '__main__':
    initialize()
