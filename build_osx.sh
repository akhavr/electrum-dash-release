#!/bin/sh
cd electrum-dash
pyrcc4 icons.qrc -o gui/qt/icons_rc.py
python setup.py sdist --format=zip,gztar
mv contrib/osx.spec .

echo -----------------
pwd
mkdir -p packages/requests
cp /usr/local/lib/python2.7/site-packages/pip/_vendor/requests/cacert.pem packages/requests/cacert.pem
cp ../python-trezor/build/scripts-2.7/trezorctl packages/trezorctl.py
pyinstaller -y --clean osx.spec
