#!/bin/sh -e

VDIR=~/build/jitfs
mkdir -p $VDIR

python3 -m venv --without-pip $VDIR

source $VDIR/bin/activate
curl https://bootstrap.pypa.io/get-pip.py | python

pip install -r /home/vagrant/jitfs/requirements.txt
pip install -r /home/vagrant/jitfs/test-requirements.txt

deactivate
