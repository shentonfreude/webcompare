#!/bin/sh
# Setup up a virtualenv and install needed packages for Hudson.
<<<<<<< HEAD
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
=======
# The python here is specific to our box called Hudson;
# we should have a more generic way of finding a python-2.6 instance.

if [ ! -f .venv/bin/activate ]
then
  virtualenv --python=/usr/bin/python26 --no-site-packages .venv
>>>>>>> 29285bca26a52351f4c5dd811d115724f883c34e
fi

source .venv/bin/activate
if [ ! .venv/bin/pip ]
then
  easy_install pip
fi

<<<<<<< HEAD
pip install -r requirements.pip

=======
if [ ! -f .venv/lib/python2.6/site-packages/lxml ]
then
  pip install -r requirements.pip
fi
>>>>>>> 29285bca26a52351f4c5dd811d115724f883c34e
exit 0

