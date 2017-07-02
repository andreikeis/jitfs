#!/bin/sh -e

VDIR=/opt/meson
mkdir -p $VDIR

python3 -m venv --without-pip $VDIR

source $VDIR/bin/activate
curl https://bootstrap.pypa.io/get-pip.py | python
pip install meson

deactivate

cd /usr/local/bin
ln -s /opt/meson/bin/meson
