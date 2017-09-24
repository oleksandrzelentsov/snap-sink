#!/usr/bin/env python3.5

import argparse
import os
import configparser
import subprocess
import logging
from sys import exit
from glob import glob
from yaml import load as y_load
from yaml import dump as y_dump

logger = logging.getLogger('snap-sync')
formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
sh = logging.StreamHandler()
sh.setFormatter(formatter)
logger.addHandler(sh)
debug = logger.debug
warning = logger.warning
info = logger.info

default_config_filename = '~/.sync.yml'
config_settings = [
    'host',
    'local',
    'remote',
    'user',
    'private_key'
]
essential_settings = [0, 1, 2, 3]


def is_option_essential(option):
    """
    Is option essential for file sync?
    """
    return config_settings.index(option) in essential_settings


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
        args_download = [
            'rsync',
            '-h',
            '--update',
            '--partial',
            ('{}@'.format(self.user) if self.user else '') + \
            '{}:{}'.format(self.host, self.remote),
            '{}'.format(self.local)
        ]
        if self.private_key:
            args_download.insert(2, "-e ssh -i {}".format(self.private_key))
        debug('running command {}'.format(' '.join(args_download)))
        p = subprocess.Popen(args_download)
        p.wait()
        args_upload = [
            'rsync',
            '-h',
            '--update',
            '--partial',
            '{}'.format(self.local),
            ('{}@'.format(self.user) if self.user else '') + \
            '{}:{}'.format(self.host, self.remote)
        ]
        if self.private_key:
            args_upload.insert(2, "-e ssh -i {}".format(self.private_key))
        debug('running command {}'.format(' '.join(args_upload)))
        p = subprocess.Popen(args_upload)
        p.wait()

    def __dict__(self):
        scope = locals()
        scope.update(globals())
        return {k: eval('self.{}'.format(k), scope) for k in config_settings}

    @staticmethod
    def expand_wildcards(sync_files):
        """
        Expands wildcards to individual SyncFiles.
        """
        result = []
        for r in sync_files:
            if '*' in r.local:
                debug("{} has * in it, expanding".format(r.local))
                files = set(glob(os.path.expanduser(r.local))) - {'.'}
                debug("expanded to [{}] using glob".format(', '.join(files)))
                dict_obj = r.__dict__()
                for f in files:
                    t = {k: dict_obj[k] for k in config_settings if k != 'local'}
                    t['local'] = f
                    t['remote'] = os.path.join(t['remote'], f.split('/')[-1])
                    result.append(SyncFile(**t))
                if len(files) == 0:
                    warning('glob pattern for {} expanded to nothing'.format(r.local))
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
        for section in sections:
            sec_o = config[section]
            args = {k: sec_o[k]
                    for k in filter(is_option_essential, config_settings)}
            for opt in filter(lambda x: not is_option_essential(x),
                              config_settings):
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
            info('file is already in yaml')
        cp = configparser.ConfigParser()
        with open(filename, 'r') as cf:
            cp.readfp(cf.readlines())
        dr = {}
        for section in cp.sections():
            dr[section] = {}
            for opt in filter(is_option_essential, config_settings):
                dr[section][opt] = cp.get(section, opt)
            for opt in filter(lambda x: not is_option_essential(x), config_settings):
                try:
                    dr[section][opt] = cp.get(section, opt)
                except:
                    debug('no {} in {}'.format(opt, section))
        n_fn, _ = os.path.splitext(filename)
        n_fn = n_fn + '.yml'
        with open(n_fn, 'w') as cf:
            info(y_dump(dr, default_flow_style=False), file=cf, end='')


def get_args():
    """
    Parse snapsink CLI arguments.
    """
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
                        default=default_config_filename,
                        help='ability to specify the sync settings \
                              file (default is {})'.format(
                            default_config_filename))
    parser.add_argument('--convert-old-config',
                        action='store_true',
                        default=False,
                        help='convert old config format (INI) to new one (YAML)')
    parser.add_argument('--level',
                        type=str,
                        default='INFO',
                        help='the logging level')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    logger.setLevel(args.level)
    if args.convert_old_config:
        SyncFile.convert_ini_to_yml(args.settings)
        exit(0)
    cp = None
    try:
        with open(os.path.expanduser(args.settings)) as config_file:
            cp = y_load(''.join(config_file.readlines()))
    except FileNotFoundError as e:
        info('No config file ({})'.format(args.settings))
        exit(1)
    files = SyncFile.from_config(cp, args.files, args.private_key)
    for file_ in files:
        if not args.silent:
            info('Syncing {} with {}@{}:{}...'.format(file_.local, file_.user, file_.host, file_.remote))
        file_.sync()
