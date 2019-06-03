# File watcher
## Description
This program can watch a directory for file changes (modify/create) and performs an action on
the files.
Files can be included/excluded using standard python regex.

## Usage
If the program is started with no options it will use the values defined in `config.yml`.
You can configure all the options from this file.

NOTE: Command line arguments will override values from `config.yml`.

Command line usage can be seen by running the program with `-h` or `--help` as
argument.

## Dependencies
- PyYAML (config file parsing)
- watchdog (Filesystem events monitoring)
- PyInstaller (`optional` executable creation)

## Change log
- starting with `v0.2`, `config.yml` will be automatically reloaded (after being updated) without
the need to restart the utility.