#!/bin/sh
cd electrum-dash
pyrcc4 icons.qrc -o gui/qt/icons_rc.py
python setup.py sdist --format=zip,gztar
pyinstaller -y --clean contrib/osx.spec
