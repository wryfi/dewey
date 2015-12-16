#!/bin/bash

if [ -z "$VIRTUALENV" ]; then
    VIRTUALENV="$HOME/.virtualenv"
fi

if [ -z "$MODULE_ROOT" ]; then
    MODULE_ROOT="$HOME/dewey/modules"
fi

if [ -z "$ENVFILE" ]; then
    ENVFILE="$HOME/etc/environment"
fi

export PYTHONPATH=$MODULE_ROOT:$PYTHONPATH

. $VIRTUALENV/bin/activate
. $ENVFILE

pushd $MODULE_ROOT
if [ $1 = worker ]; then
    exec $VIRTUALENV/bin/celery worker -A dewey -E -l info --pidfile=$HOME/var/run/worker.pid
elif [ $1 = beat ]; then
    exec $VIRTUALENV/bin/celery beat -A dewey -l info --pidfile=$HOME/var/run/beat.pid
fi
popd
