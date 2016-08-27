# snap-sink
File syncronization (using rsync)

# Features
1. File syncronization via ssh & rsync. (back&forth)
2. Configuration settings are stored in file (~/.sync.yml by default)
3. Ability to specify groups of files that should be synced via CLI.
4. Syncing deletions (_coming soon_)

# Help
```
usage: sink.py [-h] [-s] [-p PRIVATE_KEY] [--settings SETTINGS]
               [--convert-old-config]
               [files [files ...]]

Sync files between two hosts.

positional arguments:
  files                 files (sections from config file) which need to be
                        synced

optional arguments:
  -h, --help            show this help message and exit
  -s, --silent          be silent, do not output descriptional information
                        about what is done
  -p PRIVATE_KEY, --private-key PRIVATE_KEY
                        the identity file for ssh
  --settings SETTINGS   ability to specify the sync settings file (default is
                        ~/.sync.yml)
  --convert-old-config  convert old config format (INI) to new one (YAML)

```

