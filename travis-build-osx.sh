#!/bin/bash
git clone https://github.com/akhavr/electrum-dash.git electrum-dash
cd electrum-dash

protobuf_path=/usr/local/lib/python2.7/site-packages/google
sudo mkdir -p $protobuf_path
sudo touch $protobuf_path/__init__.py
sudo pip2 install protobuf==2.6.1

sudo pip2 install \
    dnspython==1.12.0 \
    slowaes==0.1a1 \
    ecdsa==0.13 \
    requests==2.5.1 \
    six==1.11.0 \
    qrcode==5.1 \
    pbkdf2==1.3 \
    jsonrpclib==0.1.7 \
    x11_hash>=1.4

pyrcc4 icons.qrc -o gui/qt/icons_rc.py
python2 setup.py sdist --format=zip,gztar

mv contrib/osx.spec .
mkdir -p packages/requests
cp /usr/local/lib/python2.7/site-packages/requests/cacert.pem packages/requests/

cp ../python-trezor/build/scripts-2.7/trezorctl packages/trezorctl.py

pyinstaller -y --clean osx.spec

sudo hdiutil create -fs HFS+ -volname "Electrum-DASH" \
    -srcfolder dist/Electrum-DASH.app dist/electrum-dash-macosx.dmg
