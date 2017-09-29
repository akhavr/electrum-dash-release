#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import sys
import time
import getpass
import shutil
import hashlib
import tempfile
import json
from subprocess import check_output

try:
    import click
    import gnupg
    import dateutil.parser
    import colorama
    from colorama import Fore, Style
    from github_release import get_releases, gh_asset_download, gh_asset_upload
except ImportError, e:
    print 'Import error:', e
    print 'To run script install required packages with the next command:\n\n' \
          'pip install githubrelease python-gnupg pyOpenSSL cryptography idna' \
          ' certifi python-dateutil click colorama'
    sys.exit(1)


HOME_DIR = os.path.expanduser('~')
CONFIG_NAME = '.sign-releases'
SEARCH_COUNT = 6
SHA_FNAME = 'SHA256SUMS.txt'


def compare_published_times(a, b):
    """Releases list sorting comparsion function"""

    a_published = a['published_at']
    b_published = b['published_at']

    if not a_published:
        return -1

    if not b_published:
        return 1

    a = dateutil.parser.parse(a_published)
    b = dateutil.parser.parse(b_published)

    if a > b:
        return -1
    elif b > a:
        return 1
    else:
        return 0


def sha256_checksum(filename, block_size=65536):
    """Gather sha256 hash on filename"""
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()


def read_config():
    """Read and parse JSON from config file from HOME dir"""
    config_path = os.path.join(HOME_DIR, CONFIG_NAME)
    if not os.path.isfile(config_path):
        return {}

    try:
        with open(config_path, 'r') as f:
            data = f.read()
            return json.loads(data)
    except Exception, e:
        print 'Error: Cannot read config file:', e
        return {}


def check_github_repo(remote_name='origin'):
    """Try to determine and return 'username/repo' if current dir is git dir"""
    try:
        remotes = check_output(['git', 'remote', '-v'],
                               stderr=open(os.devnull, 'w'))
        remotes = remotes.splitlines()
    except:
        remotes = []
    remotes = [r for r in remotes if remote_name in r]
    remotes = [r for r in remotes if '(push)' in r]
    repo = remotes[0].split()[1] if len(remotes) > 0 else None

    if repo:
        if repo.startswith('git'):
            repo = repo.split(':')[-1]

        if repo.startswith('http'):
            repo = repo.split('/')
            repo = '/'.join(repo[-2:])

    return repo


class ChdirTemporaryDirectory(object):
    """Create tmp dir, chdir to it and remove on exit"""
    def __enter__(self):
        self.name = tempfile.mkdtemp()
        os.chdir(self.name)
        return self.name

    def __exit__(self, exc_type, exc_value, traceback):
        shutil.rmtree(self.name)


class SignApp(object):
    def __init__(self, **kwargs):
        """Get app settings from options, from curdir git, from config file"""
        ask_passphrase = kwargs.pop('ask_passphrase', None)
        self.repo = kwargs.pop('repo', None)
        self.token = kwargs.pop('token', None)
        self.keyid = kwargs.pop('keyid', None)
        self.count = kwargs.pop('count', None)
        self.dry_run = kwargs.pop('dry_run', None)

        repo = check_github_repo()
        self.repo = self.repo or repo

        self.config = read_config()
        self.repo = self.repo or self.config.get('repo', None)
        self.token = self.token or self.config.get('token', None)
        self.keyid = self.keyid or self.config.get('keyid', None)
        self.count = self.count or self.config.get('count', None) \
                     or SEARCH_COUNT

        if not self.repo:
            print 'no repo found, exit'
            sys.exit(0)

        if self.token:
            os.environ['GITHUB_TOKEN'] = self.token

        if not os.environ.get('GITHUB_TOKEN', None):
            print 'GITHUB_TOKEN environment var not set, exit'
            sys.exit(0)

        self.keyid = self.keyid.split('/')[-1]

        self.passphrase = None
        self.gpg = gnupg.GPG()

        for k in self.gpg.list_keys(True):
            if not self.keyid:
                self.keyid = k.get('keyid', None)
            if self.keyid and self.keyid in k.get('keyid', ''):
                self.uid = ', '.join(k.get('uids', ['No uid found']))
                break

        if not self.keyid:
            print 'no key found, exit'
            sys.exit(0)

        if ask_passphrase:
            while not self.passphrase:
                self.read_passphrase()
        elif not self.check_key():
            while not self.passphrase:
                self.read_passphrase()

    def read_passphrase(self):
        """Read passphrase for gpg key until check_key is passed"""
        passphrase = getpass.getpass('%sInput passphrase for Key: %s %s:%s ' %
                                     (Fore.GREEN,
                                     self.keyid,
                                     self.uid,
                                     Style.RESET_ALL))
        if self.check_key(passphrase):
            self.passphrase = passphrase

    def check_key(self, passphrase=None):
        """Try to sign test string, and if some data signed retun True"""
        signed_data = self.gpg.sign('test message to check passphrase',
                         keyid=self.keyid, passphrase=passphrase)
        if signed_data.data:
            return True
        print '%sWrong passphrase!%s' % (Fore.RED, Style.RESET_ALL)
        return False

    def sign_file_name(self, name, detach=True):
        """Sign file with self.keyid, place signature in deteached .asc file"""
        with open(name, 'rb') as fdrb:
            signed_data = self.gpg.sign_file(fdrb,
                                             keyid=self.keyid,
                                             passphrase=self.passphrase,
                                             detach=detach)
            with open('%s.asc' %name, 'w') as fdw:
                fdw.write(signed_data.data)

    def sign_release(self, release, other_names, asc_names):
        """Download/sign unsigned assets, upload .asc counterparts.
        Create SHA256SUMS.txt with all assets included and upload it
        with SHA256SUMS.txt.asc counterpart.
        """
        repo = self.repo
        tag = release['tag_name']

        with ChdirTemporaryDirectory() as tmpdir:
            with open(SHA_FNAME, 'w') as fdw:
                for name in other_names:
                    if name == SHA_FNAME:
                        continue

                    gh_asset_download(repo, tag, name)
                    if not '%s.asc' % name in asc_names:
                        self.sign_file_name(name)
                        gh_asset_upload(repo, tag, '%s.asc' %name,
                                        dry_run=self.dry_run)

                    sumline = '%s %s\n' % (sha256_checksum(name), name)
                    fdw.write(sumline)

            gh_asset_upload(repo, tag, SHA_FNAME, dry_run=self.dry_run)
            self.sign_file_name(SHA_FNAME, detach=False)
            gh_asset_upload(repo, tag, '%s.asc' % SHA_FNAME,
                            dry_run=self.dry_run)

    def search_and_sign_unsinged(self):
        """Search through last 'count' releases with assets without
        .asc counterparts or releases withouth SHA256SUMS.txt.asc
        """
        releases = get_releases(self.repo)
        # cycle through releases sorted by by publication date
        releases.sort(compare_published_times)
        for r in releases[:self.count]:
            asset_names = [a['name'] for a in r['assets']]
            asc_names = [a for a in asset_names if a.endswith('.asc')]
            other_names = [a for a in asset_names if not a.endswith('.asc')]
            need_to_sign = False

            if asset_names and not asc_names:
                need_to_sign = True

            if not need_to_sign:
                for name in other_names:
                    if not '%s.asc' % name in asc_names:
                        need_to_sign = True
                        break

            if not need_to_sign:
                need_to_sign = '%s.asc' % SHA_FNAME not in asc_names

            if need_to_sign:
                self.sign_release(r, other_names, asc_names)


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-c', '--count', type=int,
              help='Number of last releases to sign')
@click.option('-k', '--keyid',
              help='gnupg keyid')
@click.option('-n', '--dry-run', is_flag=True,
              help='Do not uload signed files')
@click.option('-p', '--ask-passphrase', is_flag=True,
              help='Ask to enter passphrase')
@click.option('-r', '--repo',
              help='Repository in format username/reponame')
@click.option('-s', '--sleep', type=int,
              help='Sleep number of seconds before signing')
@click.option('-t', '--token',
              help='GigHub access token, to be set as'
                   ' GITHUB_TOKEN environmet variable')
def main(**kwargs):
    app = SignApp(**kwargs)

    sleep = kwargs.pop('sleep', None)
    if (sleep):
        print 'Sleep for %s seconds' % sleep
        time.sleep(sleep)

    app.search_and_sign_unsinged()


if __name__ == '__main__':
    colorama.init()
    main()
