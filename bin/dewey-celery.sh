#!/bin/bash

runner=$(whoami)
if [ "$runner" != "dewey" ]; then
  echo "You must run this script as the dewey user"
  exit 1
fi

if [ -z "$VIRTUALENV" ]; then
    VIRTUALENV="$HOME/.virtualenv"
fi

if [ -z "$MODULE_ROOT" ]; then
    MODULE_ROOT="$HOME/modules"
fi

export PYTHONPATH=$MODULE_ROOT:$PYTHONPATH

# the activate script should be modified to source /etc/default/dewey for us
. $VIRTUALENV/bin/activate

WORKER_PIDFILE=$HOME/run/worker.pid
BEAT_PIDFILE=$HOME/run/beat.pid

WORKER_PIDDIR=$(dirname $WORKER_PIDFILE)
BEAT_PIDDIR=$(dirname $BEAT_PIDFILE)

[ -d $WORKER_PIDDIR ] || mkdir -p $WORKER_PIDDIR
[ -d $BEAT_PIDDIR ] || mkdir -p $BEAT_PIDDIR

pushd $MODULE_ROOT
if [ $1 = worker ]; then
    exec $VIRTUALENV/bin/celery worker -A dewey -E -l info --pidfile=$WORKER_PIDFILE
elif [ $1 = beat ]; then
    exec $VIRTUALENV/bin/celery beat -A dewey -l info --pidfile=$BEAT_PIDFILE
fi
popd
