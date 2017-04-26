#!/bin/bash
set -ev
brew update
if [ "$(which qmake)" == "" ]; then
    ./install_qt_osx.sh
fi
pip install --upgrade pip
