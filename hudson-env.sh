#!/bin/sh
# Setup up a virtualenv and install needed packages for Hudson.
# The python here is specific to our box called Hudson;
# we should have a more generic way of finding a python-2.6 instance.

if [ ! -f .venv/bin/activate ]
then
  virtualenv --python=/usr/bin/python26 --no-site-packages .venv
fi

source .venv/bin/activate
if [ ! .venv/bin/pip ]
then
  easy_install pip
fi

if [ ! -f .venv/lib/python2.6/site-packages/lxml ]
then
  pip install -r requirements.pip
fi
exit 0

