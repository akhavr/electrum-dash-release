#!/bin/bash
docker build -f Dockerfile-linux -t akhavr/electrum-dash-release:Linux .
./python-trezor-wine.sh
./python-x11_hash-wine.sh
docker build -f Dockerfile-wine -t akhavr/electrum-dash-release:Wine .
