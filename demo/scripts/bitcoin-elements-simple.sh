#!/bin/bash

wget -q https://bitcoincore.org/bin/bitcoin-core-${BITCOIN_VERSION}/bitcoin-${BITCOIN_VERSION}-x86_64-linux-gnu.tar.gz

#TODO: check sha256 since it seems we can't ssl here

tar -xf bitcoin-${BITCOIN_VERSION}-x86_64-linux-gnu.tar.gz

install -m 0755 -o root -g root -t /usr/local/bin bitcoin-${BITCOIN_VERSION}/bin/*

wget -q https://github.com/ElementsProject/elements/releases/download/elements-${ELEMENTS_VERSION}/elements-${ELEMENTS_VERSION}-x86_64-linux-gnu.tar.gz

tar -xf elements-${ELEMENTS_VERSION}-x86_64-linux-gnu.tar.gz

install -m 0755 -o root -g root -t /usr/local/bin elements-${ELEMENTS_VERSION}/bin/*
