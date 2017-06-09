#!/bin/sh
cd electrum-dash
pyrcc4 icons.qrc -o gui/qt/icons_rc.py
python setup.py sdist --format=zip,gztar
mv contrib/osx.spec .
pwd
ls
pyinstaller -y --clean osx.spec
