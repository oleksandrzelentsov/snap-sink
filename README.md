# snap-sink
File syncronization (using rsync)

# Usage
```
ge: sink.py [-h] [-s] [-p PRIVATE_KEY] [--settings SETTINGS]
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
