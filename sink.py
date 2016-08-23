#!/usr/bin/env python3.5


import argparse
import os, sys
import configparser
import subprocess
import logging
from logging import debug, info
from glob import glob


config_path = '~/.sync.conf'
#logging.basicConfig(level="DEBUG")


class SyncFile(object):

    def __init__(self, host, local, remote, user=None):
        self.host = host
        self.local = os.path.expanduser(local)
        self.remote = remote
        self.user = user

    def sync(self):
        args1 = ['rsync',
                 '-h',
                 '--update',
                 '--rsh=ssh',
                 '--partial',
                 ('{}@'.format(self.user) if self.user else '') + \
                 '{}:{}'.format(self.host, self.remote),
                 '{}'.format(self.local)]
        debug('running command {}'.format(' '.join(args1)))
        p = subprocess.Popen(args1)
        p.wait()
        args2 = ['rsync',
                 '-h',
                 '--update',
                 '--rsh=ssh',
                 '--partial',
                 '{}'.format(self.local),
                 ('{}@'.format(self.user) if self.user else '') + \
                 '{}:{}'.format(self.host, self.remote)]
        debug('running command {}'.format(' '.join(args2)))
        p = subprocess.Popen(args2)
        p.wait()

    @classmethod
    def from_config(cls, config, sections):
        result = []
        if '*' in sections:
            debug('sending all files desctibed in config')
            sections = config.sections()
        elif not set(sections).issubset(set(config.sections())):
            raise Exception('Some sections are not found in config file')
            sys.exit(1)
        for section in sections:
            args = [config.get(section, 'host'),
                    config.get(section, 'local'),
                    config.get(section, 'remote'),
                    config.get(section, 'user')]
            debug('section\'s args: [{}]'.format(', '.join(args)))
            if '*' in args[1]:
                debug("{} has * in it, expanding".format(args[1]))
                files = set(glob(os.path.expanduser(args[1]))) - set(['.'])
                debug("expanded to [{}] using glob".format(', '.join(files)))
                files2 = [args[0:1] + [f] + args[2:] for f in files]
                for f in files2:
                    result.append(cls(*f))
            else:
                result.append(cls(*args))
        return result



def get_args():
    global config_path
    parser = argparse.ArgumentParser(description='Sync files between two hosts.')
    parser.add_argument('files',
                        type=str,
                        nargs='*',
                        default='*',
                        help='files (sections from config file) which need to be synced')
    parser.add_argument('-s', '--silent',
                        action='store_const',
                        const=True,
                        default=False,
                        help='be silent, do not output descriptional information about what is done')
    parser.add_argument('--settings',
                        metavar='',
                        dest='settings',
                        default=config_path)
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    cp = configparser.ConfigParser()
    with open(os.path.expanduser(args.settings)) as config_file:
        cp.readfp(config_file)
    files = SyncFile.from_config(cp, args.files)
    for file_ in files:
        if not args.silent:
            print('Syncing {} with {}@{}:{}...'.format(file_.local, file_.user, file_.host, file_.remote))
        file_.sync()

