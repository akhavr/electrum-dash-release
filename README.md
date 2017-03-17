# Electrum-DASH release scripts

## Linux

```
$ docker build -f Dockerfile-linux -t akhavr/electrum-dash-release:Linux .
$ git clone git@github.com:dashpay/electrum-dash.git
$ docker run --rm -v $(pwd):/opt \
    -w /opt/electrum-dash -t akhavr/electrum-dash-release:Linux \
    /opt/build_linux.sh
```
	
Installation:

```
$ sudo apt-get install -y python-qt4 libusb-1.0.0-dev libudev-dev
$ pip install Electrum-DASH-2.6.4.tar.gz
```

Uninstallation:

```
$ pip uninstall -y Electrum-DASH
```
