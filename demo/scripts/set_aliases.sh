#!/bin/bash
DIR=/demo/data
shopt -s expand_aliases
alias b-dae="bitcoind -datadir=$DIR/btc"
alias b-cli="bitcoin-cli -datadir=$DIR/btc"
alias b2-dae="bitcoind -datadir=$DIR/btc2"
alias b2-cli="bitcoin-cli -datadir=$DIR/btc2"
alias e1-dae="elementsd -datadir=$DIR/liquid1"
alias e1-cli="elements-cli -datadir=$DIR/liquid1"
alias e2-dae="elementsd -datadir=$DIR/liquid2"
alias e2-cli="elements-cli -datadir=$DIR/liquid2"
alias e3-dae="elementsd -datadir=$DIR/liquid3"
alias e3-cli="elements-cli -datadir=$DIR/liquid3"
#alias generate="e1-cli generatetoaddress 1 $(e1-cli getnewaddress)"
generate () {
    local ADDRESS=$(e1-cli getnewaddress)
    e1-cli generatetoaddress $1 ${ADDRESS}
}
