#!/bin/bash

export DEBFULLNAME="Dewey Maintainers"
export DEBEMAIL="it-ops@plos.org"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export GIT_SSH="$DIR/bin/dewey-ssh.sh"

if ! which dch; then
    echo " * please install the devscripts package"
    exit 1
fi

if env | grep VIRTUAL_ENV; then
    echo " * deactivate, jim!";
    exit 1
fi

if [ -z "$1" ]; then
    echo " * you must provide a version number as the first argument"
    exit 1
fi

if [ -f "debian/changelog" ]; then
    rm debian/changelog
fi

dch --create --distribution stable -v "$1" --package dewey "this file is not maintained"
dpkg-buildpackage -b -us -uc

