#!/bin/bash
git clone https://github.com/dashpay/electrum-dash.git
brew info PyQt
pyrcc4 icons.qrc -o gui/qt/icons_rc.py
python setup.py sdist --format=zip,gztar
