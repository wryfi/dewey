#!/bin/bash


runner=$(whoami)
if [ "$runner" != "dewey" ]; then
  echo "You must run this script as the dewey user"
  exit 1
fi

NAME="dewey" # Name of the application
MODULE_ROOT="$HOME/modules" # Django project directory
SOCKFILE="$HOME/run/gunicorn.sock" # we will communicte using this unix socket
USER=dewey # the user to run as
GROUP=dewey # the group to run as
NUM_WORKERS=5 # how many worker processes should Gunicorn spawn
DJANGO_WSGI_MODULE=dewey.wsgi # WSGI module name
VIRTUALENV="$HOME/.virtualenv"
 
echo "Starting $NAME as `whoami`"
 
export PYTHONPATH=$MODULE_ROOT:$PYTHONPATH

RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# Activate the virtual environment;
# the activate script should be modified to source /etc/default/dewey for us
. $VIRTUALENV/bin/activate
 
# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec $VIRTUALENV/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
--name $NAME \
--workers $NUM_WORKERS \
--user=$USER --group=$GROUP \
--bind=unix:$SOCKFILE \
--log-file=-
