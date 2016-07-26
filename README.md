# snap-sink
File syncronization (using rsync)

# Usage
```
usage: sink [-h] [--files [FILES [FILES ...]]] [-s] [--settings SETTINGS]

Sync files between two hosts.

optional arguments:
  -h, --help            show this help message and exit
  --files [FILES [FILES ...]]
                        files (sections from config file) which need to be
                        synced
  -s, --silent          be silent, do not output descriptional information
                        about what is done
  --settings SETTINGS   ability to specify the sync settings file (default is
                        ~/.sync.conf)
```
