#!/bin/bash
shopt -s expand_aliases
DIR=/demo

alias b-dae="bitcoind -datadir=$DIR/data/btc"
alias b-cli="bitcoin-cli -datadir=$DIR/data/btc"
alias e1-dae="elementsd -datadir=$DIR/data/liquid1"
alias e1-cli="elements-cli -datadir=$DIR/data/liquid1"
alias e2-dae="elementsd -datadir=$DIR/data/liquid2"
alias e2-cli="elements-cli -datadir=$DIR/data/liquid2"
alias e3-dae="elementsd -datadir=$DIR/data/liquid3"
alias e3-cli="elements-cli -datadir=$DIR/data/liquid3"
alias generate1="e1-cli generatetoaddress 1 $(e1-cli getnewaddress)"
alias generate2="e2-cli generatetoaddress 1 $(e2-cli getnewaddress)"
alias generate3="e3-cli generatetoaddress 1 $(e3-cli getnewaddress)"
