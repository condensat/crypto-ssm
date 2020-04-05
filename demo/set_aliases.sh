#!/bin/bash
shopt -s expand_aliases
alias b-dae="bitcoind -datadir=$PWD/data/btc"
alias b-cli="bitcoin-cli -datadir=$PWD/data/btc"
alias e1-dae="elementsd -datadir=$PWD/data/liquid1"
alias e1-cli="elements-cli -datadir=$PWD/data/liquid1"
alias e2-dae="elementsd -datadir=$PWD/data/liquid2"
alias e2-cli="elements-cli -datadir=$PWD/data/liquid2"
alias e3-dae="elementsd -datadir=$PWD/data/liquid3"
alias e3-cli="elements-cli -datadir=$PWD/data/liquid3"
alias generate="e1-cli generatetoaddress 1 $(e1-cli getnewaddress)"
