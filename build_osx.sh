#!/bin/sh
cd electrum-dash
pyrcc4 icons.qrc -o gui/qt/icons_rc.py
python setup.py sdist --format=zip,gztar
mv contrib/osx.spec .

echo -----------------
pwd
find .. -name packages
pyinstaller -y --clean osx.spec
