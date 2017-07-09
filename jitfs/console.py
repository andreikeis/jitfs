from __future__ import print_function

import os
import sys
import click
import logging
import yaml

# from gevent import server as gserver  # pylint: disable=F401
# from gevent import socket  # pylint: disable=F401

import jitfs

from jitfs.backend import local

_LOGGER = logging.getLogger(__name__)


logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.DEBUG
)


def make_local_provider(cache_db):
    return local.JitfsLocalBackend(cache_db)


_PROVIDERS = {
    'local': make_local_provider,
}


@click.group()
def run():
    pass


@run.group(chain=True)
def backend():
    """Manage jitfs backend configuration."""
    pass


@backend.resultcallback()
def backend_resultclbk(configs):
    """Output combined backend configuration."""
    combined = {}
    for config in configs:
        combined.update(config)
    yaml.dump(combined,
              stream=sys.stdout,
              default_flow_style=False,
              explicit_start=True,
              explicit_end=False)


@backend.command(name='local')
@click.option('--cache-db', required=True,
              help='Path to cache database.')
def local_cmd(cache_db):
    """Local provider configuration."""
    return {'local': {'cache_db': cache_db}}


@run.command()
@click.option('--cache', help='Path to cache.',
              required=True)
@click.option('--backend', help='Jitfs backend plugin',
              required=True,
              type=click.Choice(_PROVIDERS))
@click.option('--backend-config', help='Jitfs backend configuration',
              type=click.File(mode='r'))
@click.argument('socket_path')
def server(cache, backend, backend_config, socket_path):
    """Run jitfs server."""
    _LOGGER.info('Starting server: cache: %s, socket: %s',
                 cache, socket_path)
    config = yaml.load(backend_config.read())
    kwargs = config.get(backend, {})

    provider = _PROVIDERS[backend](**kwargs)
    jitfs.run_server(cache, socket_path, provider)


@run.command()
@click.argument('socket_path')
@click.argument('cache')
@click.argument('checksum')
def request(socket_path, cache, checksum):
    """Request checksum."""

    part1 = checksum[0:2]
    part2 = checksum[2:4]
    cache_path = os.path.join(cache, part1, part2, checksum)

    if os.path.exists(cache_path):
        _LOGGER.info('Cache file exists: %s', cache_path)
        return

    jitfs_client = jitfs.JitfsClient(socket_path)
    jitfs_client.request(checksum)

    if os.path.exists(cache_path):
        _LOGGER.info('Cache fetched successdully: %s, %s',
                     cache_path, os.path.exists(cache_path))


@run.command()
@click.option('--backend', help='Jitfs backend plugin',
              required=True,
              type=click.Choice(_PROVIDERS))
@click.option('--backend-config', help='Jitfs backend configuration',
              type=click.File(mode='r'))
@click.option('--mirror', help='Path to mirror directory.',
              required=True)
@click.option('--mirror-db', help='Path to mirror db.',
              required=True)
@click.option('--rel-path', help='Use relative path for jitfs symlinks.',
              is_flag=True, default=False)
@click.option('--root', default='/')
@click.argument('source')
def checkout(backend, backend_config, mirror, mirror_db, rel_path, root,
             source):
    """Checkout local directory."""
    kwargs = yaml.load(backend_config.read()).get(backend, {})
    provider = _PROVIDERS[backend](**kwargs)

    jitfs.checkout(provider, mirror, mirror_db, root, source, rel_path)
