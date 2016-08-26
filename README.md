# snap-sink
File syncronization (using rsync)

# Usage
```
usage: sink.py [-h] [-s] [-p PRIVATE_KEY] [--settings SETTINGS]
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
                        ~/.sync.conf)

```
