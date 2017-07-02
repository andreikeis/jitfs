#!/bin/sh

NINJA_URL=https://github.com/ninja-build/ninja/releases/download/v1.7.2/ninja-linux.zip

mkdir -p /opt/ninja/bin
wget -qO- $NINJA_URL | zcat > /opt/ninja/bin/ninja
chmod +x /opt/ninja/bin/ninja
cd /usr/local/bin
ln -s /opt/ninja/bin/ninja
