import os
import sys
import yaml
import logging
import re
from typing import Dict
from watchdog.observers.polling import PollingObserver as Observer
from EventHandler import EventHandler
import actions


# configuration file must be placed in the same directory with the script
_CONFIG_FILE = 'config.yml'
CONFIG_CHANGED = 0
STOP_WATCHER = 1


class WatcherConfig:
    config_objects = []

    def __init__(self):
        # get config file path relative to the script's path
        tmp_path = os.path.dirname(sys.argv[0])
        tmp_path = os.path.abspath(tmp_path)
        self.config_path = os.path.join(tmp_path, _CONFIG_FILE)
        yml_config = self.get_yml_config()
        for config in yml_config["watchers"]:
            self.config_objects.append(ConfigObject(config))

    def get_yml_config(self):
        yml_config: Dict = None
        if not os.path.isfile(self.config_path):
            logging.warning(f"Configuration file '{self.config_path}' does not exist!")
        else:
            with open(self.config_path, 'r') as config_file:
                yml_config = yaml.load(config_file, Loader=yaml.BaseLoader)
        return yml_config


def expand_env_var(str_var):
    pattern = r'\${([\w-]+)}'
    matches = re.finditer(pattern, str_var)
    for match in matches:
        env_var_name = match.group(1)
        env_var_pattern = r'\${(' + env_var_name + r')}'
        env_var_value = os.getenv(env_var_name, default="")
        str_var = re.sub(env_var_pattern, env_var_value, str_var)
    return str_var


class ConfigObject:
    def __init__(self, yml_config: Dict):
        self.watch_path = '.'
        self.action = {'name': 'default', 'args': []}
        self.__include_list = []
        self.__exclude_list = []
        self.observer_timeout = 0.5
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
            self.watch_path = expand_env_var(self.watch_path)
        if 'action' in yml_config:
            self.action = yml_config['action']
        if 'observer_timeout' in yml_config:
            self.observer_timeout = yml_config['observer_timeout']

    @property
    def include_list(self):
        return self.__include_list

    @property
    def exclude_list(self):
        return self.__exclude_list


class WatcherObject:
    def __init__(self, config):
        self.action_name = config.action['name']
        self.action_args = config.action['args']
        self.watch_path = config.watch_path
        self.action = actions.ACTION_LIST[self.action_name].a_class
        self.event_handler = EventHandler(
            config, self.action(self.action_args))
        logging.info(
            f"[event_id:{self.event_handler.event_id}]; watch_path:{self.watch_path}")
        observer_timeout = config.observer_timeout
        self.observer = Observer(timeout=observer_timeout)

    def start(self):
        self.observer.schedule(
            self.event_handler, self.watch_path, recursive=False)
        self.observer.start()


LOG_LEVELS = {
    'notset': logging.NOTSET,
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}


def initialize(log_level):
    FORMAT = "[%(asctime)s][%(levelname)s] %(message)s"
    DATEFMT = "%d-%m-%Y %H:%M:%S"
    logging.basicConfig(format=FORMAT, level=LOG_LEVELS[log_level])
