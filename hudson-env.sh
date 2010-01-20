#!/bin/sh
# Setup up a virtualenv and install needed packages for Hudson.
# We try various python-2.6 names including the environment var PYTHON.

if [ ! $PYTHON ]
then
    PYTHON=`which python2.6`
    if [ ! $PYTHON ]
    then
	PYTHON=`which python26`
    fi
fi
if [ ! -x $PYTHON ] 
then
    echo "ERROR couldn't find executable python-2.6 in python2.6 or python26; set environment PYTHON to its path."
    exit 1
fi
echo "Using python-2.6 found at: $PYTHON"

if [ ! -f .venv/bin/activate ]
then
  virtualenv=`dirname $PYTHON`/virtualenv
  if [ ! -f $virtualenv ]
  then
      echo "ERROR: no virtualenv found in python's binary path at $virtualenv, please easy_install it"
      exit 1
  fi
  $virtualenv --python=$PYTHON --no-site-packages .venv
fi

source .venv/bin/activate
if [ ! .venv/bin/pip ]
then
  easy_install pip
fi

pip install -r requirements.pip

exit 0

