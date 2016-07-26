#!/usr/bin/env python


import argparse
import os, sys
import ConfigParser
import subprocess


config_path = '~/.sync.conf'


class SyncFile(object):

    def __init__(self, host, local, remote, user=None):
        self.host = host
        self.local = os.path.expanduser(local)
        self.remote = remote
        self.user = user

    def sync(self):
        p = subprocess.Popen(['rsync',
                              '-h',
                              '--update',
                              '--rsh=ssh',
                              '--partial',
                              ('{}@'.format(self.user) if self.user else '') + \
                              '{}:{}'.format(self.host, self.remote),
                              '{}'.format(self.local)])
        p.wait()
        p = subprocess.Popen(['rsync',
                              '-h',
                              '--update',
                              '--rsh=ssh',
                              '--partial',
                              '{}'.format(self.local),
                              ('{}@'.format(self.user) if self.user else '') + \
                              '{}:{}'.format(self.host, self.remote)])
        p.wait()

    @classmethod
    def from_config(cls, config, sections):
        result = []
        if '*' in sections:
            sections = config.sections()
        elif not set(sections).issubset(set(config.sections())):
            raise Exception('Some sections are not found in config file')
            sys.exit(1)
        for section in sections:
            result.append(cls(config.get(section, 'host'),
                              config.get(section, 'local'),
                              config.get(section, 'remote'),
                              config.get(section, 'user')))
        return result



def get_args(rcfiles):
    parser = argparse.ArgumentParser(description='Sync files between two hosts.')
    parser.add_argument('--files',
                        type=str,
                        choices=rcfiles,
                        nargs='*',
                        default='*',
                        required=False,
                        help='files (sections from config file) which need to be synced')
    parser.add_argument('-s', '--silent',
                        action='store_const',
                        const=True,
                        default=False,
                        help='be silent, do not output descriptional information about what is done')
    return parser.parse_args()


if __name__ == '__main__':
    cp = ConfigParser.ConfigParser()
    with open(os.path.expanduser(config_path)) as config_file:
        cp.readfp(config_file)
    sections = cp.sections()
    args = get_args(sections)
    files = SyncFile.from_config(cp, args.files)
    for file_ in files:
        if not args.silent:
            print 'Syncing {} with {}@{}:{}...'.format(file_.local, file_.user, file_.host, file_.remote)
        file_.sync()

