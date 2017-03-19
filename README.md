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

## Windows (WINE)

```
$ ./python-trezor-wine.sh
$ ./python-x11_hash-wine.sh
$ docker build -f Dockerfile-wine -t akhavr/electrum-dash-release:Wine .
$ git clone git@github.com:dashpay/electrum-dash.git
$ docker run --rm -v $(pwd):/opt \
    -v $(pwd)/electrum-dash/:/root/.wine/drive_c/electrum \
    -w /opt/electrum-dash -t akhavr/electrum-dash-release:Wine \
    /opt/build_wine.sh
```
