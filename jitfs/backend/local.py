"""Local backend for jitfs."""

import logging

import sqlite3 as sqlite

from jitfs import utils

_LOGGER = logging.getLogger(__name__)


class JitfsLocalBackend(object):
    """Jitfs over existing local filesystem."""

    _CREATE_TABLE_SQL = (
        '''CREATE TABLE IF NOT EXISTS files (checksum TEXT PRIMARY KEY,
                                             path TEXT)''')
    _INSERT_PATH_SQL = (
        '''INSERT OR IGNORE INTO files (checksum, path) VALUES (?, ?)''')

    _SELECT_PATH_SQL = (
        '''SELECT path FROM files WHERE checksum=?''')

    def __init__(self, cache_db):
        self.cache_db_conn = sqlite.connect(cache_db)
        self.cache_db_cur = self.cache_db_conn.cursor()
        self.cache_db_cur.execute(self._CREATE_TABLE_SQL)

    def put(self, checksum, path):
        self.cache_db_cur.execute(self._INSERT_PATH_SQL, (checksum, path, ))

    def get(self, checksum, cache_path):
        self.cache_db_cur.execute(self._SELECT_PATH_SQL, (checksum, ))
        row = self.cache_db_cur.fetchone()
        if row:
            path = row[0]
            _LOGGER.info('Found: %s - %s', checksum, path)
            utils.symlink(path, cache_path)
        else:
            _LOGGER.info('Record not found.')

    def close(self):
        self.cache_db_conn.commit()
