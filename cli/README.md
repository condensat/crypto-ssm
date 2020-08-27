# Software Security Module command line

## Setup

- python3
- wallycore

## Main program

```bash
ssm-cli --help
Usage: ssm-cli [OPTIONS] COMMAND [ARGS]...

  Crypto SSM Command-Line Interface

Options:
  -c, --chain [bitcoin-main|bitcoin-test|bitcoin-regtest|liquidv1|elements-regtest]
                                  Define the chain we're on out of a list
                                  (default = 'bitcoin-main').
  -p, --password TEXT             Key to unlock the private keys.
  -v, --verbose                   Print more information, may be used multiple
                                  times.
  --version                       Show the version and exit.
  --help                          Show this message and exit.

Commands:
  get-xprv        Get the extended private key (xprv) that corresponds to some
                  master key.
  get-xpub        Get the extended public key (xpub) that corresponds to some
                  master key.
  new-address     Generate a new address for chain and master key
  new-master      Generate a new seed and master key for the chain
  restore-master  Restore masterkey from base58 xprv
  sign-tx         Sign all or some inputs of a serialized transaction.
```