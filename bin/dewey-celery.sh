#!/bin/bash

runner=$(whoami)
if [ "$runner"  = "root" ]; then
  echo "You must not run this as root"
  exit 1
fi

if [ -z "${VIRTUALENV}" ]; then
    if [ -d "${HOME}/.virtualenv" ]; then
        VIRTUALENV="${HOME}/.virtualenv"
    elif [ -d "${HOME}/.virtualenvs/dewey" ]; then
        VIRTUALENV="${HOME}/.virtualenvs/dewey"
    elif [ -d "/opt/dewey" ]; then
        VIRTUALENV="/opt/dewey"
    else
        echo "ERROR: no virtualenv found; try setting the VIRTUALENV variable"
        exit 1
    fi
fi

# NOTE: modify the activate script to source /etc/default/dewey
. ${VIRTUALENV}/bin/activate

WORKER_PIDFILE=${HOME}/run/worker.pid
BEAT_PIDFILE=${HOME}/run/beat.pid

WORKER_PIDDIR=$(dirname ${WORKER_PIDFILE})
BEAT_PIDDIR=$(dirname ${BEAT_PIDFILE})

[ -d ${WORKER_PIDDIR} ] || mkdir -p ${WORKER_PIDDIR}
[ -d ${BEAT_PIDDIR} ] || mkdir -p ${BEAT_PIDDIR}

if [ $1 = worker ]; then
    exec ${VIRTUALENV}/bin/celery worker -A dewey.core -E -l info --pidfile=${WORKER_PIDFILE}
elif [ $1 = beat ]; then
    exec ${VIRTUALENV}/bin/celery beat -A dewey.core -l info -S django --pidfile=${BEAT_PIDFILE}
elif [ $1 = flower ]; then
    exec ${VIRTUALENV}/bin/celery flower -A dewey.core --address=127.0.0.1 --port=5555
fi
