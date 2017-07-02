#!/bin/sh

LIBFUSE_URL=https://github.com/libfuse/libfuse/archive/fuse-3.0.2.tar.gz

mkdir -p ~/libfuse
cd ~/libfuse
wget $LIBFUSE_URL
tar xvf fuse-3.0.2.tar.gz

mkdir -p libfuse-fuse-3.0.2/build
cd libfuse-fuse-3.0.2/build

/usr/local/bin/meson ..
ninja-build
ninja-build install
