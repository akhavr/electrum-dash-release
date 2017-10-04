#!/bin/bash
BUILD_REPO_URL=https://github.com/dashpay/electrum-dash-old.git

if [[ -z $TRAVIS_TAG ]] || [[ $TRAVIS_TAG == develop ]]; then
  git clone $BUILD_REPO_URL electrum-dash
else
  git clone --branch $TRAVIS_TAG $BUILD_REPO_URL electrum-dash
fi

docker run --rm -v $(pwd):/opt -w /opt/electrum-dash -t akhavr/electrum-dash-release:Linux /opt/build_linux.sh
docker run --rm -v $(pwd):/opt -v $(pwd)/electrum-dash/:/root/.wine/drive_c/electrum -w /opt/electrum-dash -t akhavr/electrum-dash-release:Wine /opt/build_wine.sh
