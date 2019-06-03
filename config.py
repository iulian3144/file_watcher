import os
import sys
import yaml
import logging
import time
from typing import Dict


# configuration file must be placed in the same directory with the script
_CONFIG_FILE = 'config.yml'
CONFIG_CHANGED = 0
STOP_WATCH = 1


class WatcherConfig:
    config_object = None

    def __init__(self):
        self.config_path = os.path.dirname(sys.argv[0])
        self.config_path = os.path.abspath(self.config_path)
        self.config_path = os.path.join(self.config_path, _CONFIG_FILE)
        yml_config = self.get_yml_config()
        self.config_object = ConfigObject(yml_config)

    def get_yml_config(self):
        yml_config: Dict = None
        if not os.path.isfile(self.config_path):
            logging.warning(f"Configuration file '{self.config_path}' does not exist!")
        else:
            with open(self.config_path, 'r') as config_file:
                yml_config = yaml.load(config_file, Loader=yaml.BaseLoader)
        return yml_config

    # blocks until configuration file changes or ^C is pressed
    def watch_configuration(self):
        last_mtime = os.path.getmtime(self.config_path)
        try:
            logging.info("Start watching configuration file...")
            while True:
                current_mtime = os.path.getmtime(self.config_path)
                if current_mtime > last_mtime:
                    logging.info("Reloading configuration file...")
                    yml_config = self.get_yml_config()
                    self.config_object.update(yml_config)
                    return CONFIG_CHANGED
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Stop watching configuration file...")
            return STOP_WATCH


class ConfigObject:
    def __init__(self, yml_config: Dict):
        self.watch_path = '.'
        self.action = 'default'
        self.action_arg = ''
        self.__include_list = []
        self.__exclude_list = []
        self.update(yml_config)

    def update(self, yml_config: Dict):
        if not yml_config:
            return
        if "include" in yml_config:
            self.__include_list = yml_config["include"]
        if "exclude" in yml_config:
            self.__exclude_list = yml_config["exclude"]
        if 'watch_path' in yml_config:
            self.watch_path = yml_config['watch_path']
        if 'action' in yml_config:
            self.action = yml_config['action']
        if 'action_arg' in yml_config:
            self.action_arg = yml_config['action_arg']

    @property
    def include_list(self):
        return self.__include_list

    @property
    def exclude_list(self):
        return self.__exclude_list
