"""Helper utility functions."""

import os


def mkdir(dirname):
    """Safely create directories."""
    try:
        os.makedirs(dirname)
    except OSError as oserr:
        pass


def symlink(tgt, link_name):
    """Creaty symlink and all subdirectories."""
    mkdir(os.path.dirname(link_name))
    try:
        os.unlink(link_name)
    except OSError as oserr:
        pass

    os.symlink(tgt, link_name)
