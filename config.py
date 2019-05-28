import os
import yaml
import logging


__CONFIG_FILE = 'config.yml'

class WatcherConfig():
    def __init__(self, config_object):
        if config_object:
            self.__include_list = config_object["include"]
            self.__exclude_list = config_object["exclude"]
        else:
            self.__include_list = []
            self.__exclude_list = []

    @property
    def include_list(self):
        return self.__include_list

    @property
    def exclude_list(self):
        return self.__exclude_list



def initialize():
    config_object = {}
    if not os.path.isfile(__CONFIG_FILE):
        logging.warn("Configuration file '{}' does not exist!".format(__CONFIG_FILE))
    else:
        with open(__CONFIG_FILE, 'r') as config_file:
            logging.info("Loading configuration...")
            config_object = yaml.load(config_file, Loader=yaml.BaseLoader)

    return WatcherConfig(config_object)



if __name__ == '__main__':
    initialize()
