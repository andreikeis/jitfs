#!/bin/sh

SCRIPTDIR=$(cd $(dirname $0) && pwd)

mount --make-rprivate /

mkdir -p ~/.provision

function run {
    checksum=~/.provision/$(basename $1)
    md5sum -c $checksum
    if [ $? -eq 0 ]; then
        echo $1 is up to date.
    else
        $1 || (echo $1 failed. && exit 1)
        md5sum $1 > $checksum
    fi
}

run $SCRIPTDIR/install-base.sh
run $SCRIPTDIR/install-meson.sh
run $SCRIPTDIR/install-libfuse.sh
run $SCRIPTDIR/configure-profile.sh

