"""Jitfs protocol implementation."""

import os
import stat
import sqlite3
import hashlib
import logging

from gevent import server as gserver
from gevent import socket

from jitfs import utils


_LOGGER = logging.getLogger(__name__)

_REPLY_DONE = b'\x00'

_REPLY_CONTINUE = b'\x01'


class JitfsServer(gserver.DatagramServer):

    def __init__(self, cache, listener, provider):
        self.cache = cache
        self.provider = provider
        super().__init__(listener=listener)

    def handle(self, data, address):
        """Handle jitfs request."""

        checksum = data.strip().decode()
        _LOGGER.info('Requested: %s, len(%s), from: %s',
                     checksum, len(checksum), address)

        part1 = checksum[0:2]
        part2 = checksum[2:4]
        cache_path = os.path.join(self.cache, part1, part2, checksum)

        if not os.access(cache_path, os.F_OK):
            self.provider.get(checksum, cache_path)

        self.socket.sendto(_REPLY_DONE, address)


def run_server(cache, socket_path, provider):
    """Start jitfs server listening on socket, given provider impl."""

    _LOGGER.info('Starting jitfs listener on: %s', socket_path)
    try:
        os.unlink(socket_path)
    except OSError as oserr:
        pass

    listener = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    listener.bind(socket_path)

    JitfsServer(cache=cache,
                listener=listener,
                provider=provider).serve_forever()


class JitfsClient(object):

    def __init__(self, socket_path):

        self.socket_path = socket_path

        reply_socket = socket_path + '.' + str(os.getpid())
        try:
            os.unlink(reply_socket)
        except OSError as oserr:
            pass

        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.sock.bind(reply_socket)

    def request(self, cache, checksum):
        """Request checksum."""
        self.sock.sendto(checksum.encode('utf-8'), self.socket_path)
        received = self.sock.recvfrom(32)

        while True:
            status = ord(received[0])
            if status == 0:
                _LOGGER.debug('Success.')
                break

            _LOGGER.debug('Continue: rc = %s', status)
            received = self.sock.recvfrom(32)


def checkout(provider, mirror, mirror_db, root, source, rel_path):
    """Checkout local directory."""
    mirror = mirror.rstrip('/')
    source = source.rstrip('/')

    if not root.endswith('/'):
        root += '/'

    mirror_db_conn = sqlite3.connect(mirror_db)
    mirror_db_cur = mirror_db_conn.cursor()

    try:
        mirror_db_cur.execute(
            '''CREATE TABLE files (checksum TEXT PRIMARY KEY,
                                   mode INT,
                                   size INT)''')
    except sqlite3.OperationalError as sqlerr:
        _LOGGER.critical('Failed to initialize mirror db: %s', sqlerr)

    def add_file(filename):
        """Add file to cache."""
        if os.path.islink(filename):
            link_name = os.path.join(mirror, filename[len(root):])
            utils.symlink(os.readlink(filename), link_name)
            return

        if not os.path.isfile(filename):
            _LOGGER.info('Ignore special file: %s', filename)
            return

        try:
            with open(filename, 'rb') as f:
                checksum = hashlib.sha256(f.read()).hexdigest()
                fstat = os.stat(filename)
                is_exe = bool(stat.S_IXUSR & fstat.st_mode)
                size = fstat.st_size
        except IOError as ioerr:
            _LOGGER.error('Unable to add file: %s, error: %s',
                          filename, ioerr)
            return

        _LOGGER.info('Adding: %s %s, exe: %s, size: %s',
                     source, checksum, is_exe, size)

        provider.put(checksum, filename)

        mirror_db_cur.execute(
            'INSERT OR IGNORE INTO files (checksum, mode, size)'
            ' values (?, ?, ?)',
            (checksum, is_exe, size,))

        link_name = os.path.join(mirror, filename[len(root):])
        if rel_path:
            jitfs_fullpath = os.path.join(mirror, '.jitfs', checksum)
            jitfs_link_tgt = os.path.relpath(
                jitfs_fullpath, os.path.dirname(link_name))
        else:
            jitfs_link_tgt = os.path.join('/.jitfs', checksum)

        _LOGGER.info('Link: %s - %s', jitfs_link_tgt, link_name)
        utils.symlink(jitfs_link_tgt, link_name)

    # Add recursively if source is directory, otherwise process one file.
    if os.path.isdir(source):
        # Walk directory structure.
        for dirpath, dirnames, filenames in os.walk(source):
            for filename in filenames:
                add_file(os.path.join(dirpath, filename))
    else:
        add_file(source)

    mirror_db_conn.commit()
    provider.close()
