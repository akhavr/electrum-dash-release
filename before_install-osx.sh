#!/bin/bash
set -ev
brew update
if [ "$(which qmake)" == "" ]; then
    ./install_qt_osx.sh
fi
# if [ "$(which sip)" == "" ]; then
#     ./install_sip_osx.sh
# fi
# if [ "$(which pyrcc4)" == "" ]; then
#     ./install_pyqt4_osx.sh
# fi
# pip install --upgrade pip
