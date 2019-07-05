import logging
import config
import argparse
from actions import ACTION_LIST


def list_actions():
    for action_name, definition in ACTION_LIST.items():
        print(f"{action_name:>10s} : {definition.a_desc}")


def init_watchers(configurations):
    watchers = []
    for watcher_config in configurations:
        watchers.append(config.WatcherObject(watcher_config))
    return watchers


def init_arg_parser():
    parser = argparse.ArgumentParser(description='File Watcher',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-l', '--list-actions', dest="list_actions", action="store_true",
                        help='list actions')
    parser.add_argument('-v', '--verbosity', dest='log_level',
                        choices=config.LOG_LEVELS.keys(), default='info',
                        help='specify verbosity level')
    return parser


def main():
    arg_parser = init_arg_parser()
    watcher_configurations = config.WatcherConfig()
    config_objects = watcher_configurations.config_objects
    args = arg_parser.parse_args()
    config.initialize(log_level=args.log_level)

    if args.list_actions:
        list_actions()
        exit()

    watchers = init_watchers(config_objects)
    [watcher.start() for watcher in watchers]

    try:
        import time
        while True:
            time.sleep(1000)
    except KeyboardInterrupt:
        logging.info("Quitting...")
        [watcher.observer.stop() for watcher in watchers]
        [watcher.observer.join() for watcher in watchers]


if __name__ == "__main__":
    main()
