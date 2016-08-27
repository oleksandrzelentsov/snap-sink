#!/usr/bin/env python3.5


import argparse
import os, sys
import configparser
import subprocess
import logging
from logging import debug
from glob import glob
from yaml import load as y_load
from yaml import dump as y_dump


#logging.basicConfig(level="DEBUG")
config_path = '~/.sync.yml'
config_file_settings = ['host',
                        'local',
                        'remote',
                        'user',
                        'private_key']
config_file_essential = [0,1,2,3]


def is_option_essential(option):
    """
    Is option essential for file sync?
    """
    return config_file_settings.index(option) in config_file_essential


class SyncFile(object):
    """
    Class that stores the info of application's grains of sand - files.
    """

    def __init__(self, host, local, remote, user=None, private_key=None):
        self.host = host
        self.local = os.path.expanduser(local)
        self.remote = remote
        self.user = user
        self.private_key = private_key

    def sync(self):
        """
        Initiate the syncronization of file.
        """
        args1 = ['rsync',
                 '-h',
                 '--update',
                 '--partial',
                 ('{}@'.format(self.user) if self.user else '') + \
                 '{}:{}'.format(self.host, self.remote),
                 '{}'.format(self.local)]
        if self.private_key:
            args1.insert(2, "-e ssh -i {}".format(self.private_key))
        debug('running command {}'.format(' '.join(args1)))
        p = subprocess.Popen(args1)
        p.wait()
        args2 = ['rsync',
                 '-h',
                 '--update',
                 '--partial',
                 '{}'.format(self.local),
                 ('{}@'.format(self.user) if self.user else '') + \
                 '{}:{}'.format(self.host, self.remote)]
        if self.private_key:
            args2.insert(2, "-e ssh -i {}".format(self.private_key))
        debug('running command {}'.format(' '.join(args2)))
        p = subprocess.Popen(args2)
        p.wait()

    def __dict__(self):
        return {k: eval('self.{}'.format(k), locals()) for k in config_file_settings}

    @staticmethod
    def expand_wildcards(syncfiles):
        """
        Expands wildcards to individual SyncFiles.
        """
        result = []
        for r in syncfiles:
            if '*' in r.local:
                debug("{} has * in it, expanding".format(r.local))
                files = set(glob(os.path.expanduser(r.local))) - set(['.'])
                debug("expanded to [{}] using glob".format(', '.join(files)))
                dict_obj = dict(r)
                for f in files:
                    t = {k: dict_obj[k] for k in config_file_settings if k != 'local'}
                    t['local'] = f
                    result.append(cls(**t))
            else:
                result.append(r)
        return result


    @classmethod
    def _handlers(cls):
        """
        All post-processing functions to execute on SyncFile
        objects list before actually returning them.
        """
        return [cls.expand_wildcards]

    @classmethod
    def from_config(cls, config, sections, private_key=None):
        """
        Create SyncFile object from config and sections list.
        """
        result = []
        if '*' in sections:
            debug('sending all files desctibed in config')
            sections = config.keys()
        elif not set(sections).issubset(set(config.keys())):
            raise Exception('Some sections are not found in config file')
            sys.exit(1)
        for section in sections:
            sec_o = config[section]
            args = {k: sec_o[k]
                    for k in filter(is_option_essential, config_file_settings)}
            for opt in filter(lambda x: not is_option_essential(x),
                              config_file_settings):
                try:
                    args[opt] = sec_o[opt]
                except:
                    if opt == 'private_key':
                        args[opt] = private_key
            result.append(cls(**args))
            debug('section\'s args: [{}]'.format(repr(args)))
        for handler in cls._handlers():
            result = handler(result)
        return result

    @staticmethod
    def convert_ini_to_yml(filename):
        """
        Convert ini file to yaml file.
        Used for old configuration files.
        """
        filename = os.path.expanduser(filename)
        if not os.path.isfile(filename):
            raise FileNotFoundError()
        elif filename.endswith('.yml'):
            print('file is already in yaml')
        cp = configparser.ConfigParser()
        with open(filename, 'r') as cf:
            cp.readfp(cf.readlines())
        dr = {}
        for section in cp.sections():
            dr[section] = {}
            for opt in filter(is_option_essential, config_file_settings):
                dr[section][opt] = cp.get(section, opt)
            for opt in filter(lambda x: not is_option_essential(x), config_file_settings):
                try:
                    dr[section][opt] = cp.get(section, opt)
                except:
                    debug('no {} in {}'.format(opt, section))
        n_fn, _ = os.path.splitext(filename)
        n_fn = n_fn + '.yml'
        with open(n_fn, 'w') as cf:
            print(y_dump(dr, default_flow_style = False), file=cf, end='')


def get_args():
    """
    Parse snapsink CLI arguments.
    """
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
    parser.add_argument('-p', '--private-key',
                        type=str,
                        help='the identity file for ssh')
    parser.add_argument('--settings',
                        default=config_path,
                        help='ability to specify the sync settings file (default is {})'.format(config_path))
    parser.add_argument('--convert-old-config',
                        action='store_true',
                        default=False,
                        help='convert old config format (INI) to new one (YAML)')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    if args.convert_old_config:
        SyncFile.convert_ini_to_yml(args.settings)
        sys.exit(0)
    cp = None
    with open(os.path.expanduser(args.settings)) as config_file:
        cp = y_load(''.join(config_file.readlines()))
    files = SyncFile.from_config(cp, args.files, args.private_key)
    for file_ in files:
        if not args.silent:
            print('Syncing {} with {}@{}:{}...'.format(file_.local, file_.user, file_.host, file_.remote))
        file_.sync()

