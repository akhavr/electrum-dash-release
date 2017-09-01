#!/bin/bash
git clone https://github.com/dashpay/electrum-dash-old.git electrum-dash
docker run --rm -v $(pwd):/opt -w /opt/electrum-dash -t akhavr/electrum-dash-release:Linux /opt/build_linux.sh
docker run --rm -v $(pwd):/opt -v $(pwd)/electrum-dash/:/root/.wine/drive_c/electrum -w /opt/electrum-dash -t akhavr/electrum-dash-release:Wine /opt/build_wine.sh
