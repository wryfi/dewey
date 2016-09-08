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

pushd $MODULE_ROOT
  ./manage.py "${@}"
popd
