import click
import json
import logging
import sys
from collections import namedtuple
import cli.exceptions as exceptions
import cli.ssm as ssm

from cli.connect import (
    ConnCtx,
    BITCOIN_REGTEST_RPC_PORT,
    LIQUID_REGTEST_RPC_PORT
)

from cli.util import (
    CHAINS,
    set_logging,
)

def critical(title='', message='', start_over=True):
    """Function to prompt critical error message

    Its interface matches requirements from ConnCtx
    """
    logging.error(message)
    if start_over:
        sys.exit(1)


ConnParams = namedtuple('ConnParams', ['chain'])


@click.group()
@click.option('-c', '--chain', default='bitcoin-main', type=click.Choice(CHAINS),
                help='Define the chain we\'re on out of a list (default = \'bitcoin-main\').')
@click.option('-v', '--verbose', count=True,
              help='Print more information, may be used multiple times.')
@click.version_option()
@click.pass_context
def cli(ctx, verbose, chain):
    """Crypto SSM Command-Line Interface
    """

    set_logging(verbose)

    logging.info(f"Working on {chain}")
    
    ctx.obj = ConnParams(chain)


@cli.command(short_help='Generate a new seed and master key for the chain')
@click.option('-e', '--entropy', required=True,
                help='Either a password or some entropy to use for seed generation.')
@click.option('-b', 'isbytes', is_flag=True,
                help='If set, entropy is to be treated as an hex byte string rather than a password.')
@click.pass_obj
def new_master(obj, entropy, isbytes):
    """Generate a new seed and the corresponding master key for BIP32 derivation.
    The new seed can use either a password and a salt, or some entropy (at least 32B).
    At least one of 2 is required.
    Return value is the fingerprint of the new master key.
    """

    logging.info(f"Generating a new master key for {obj.chain}.")

    fingerprint = ssm.generate_new_hd_wallet(obj.chain, entropy, isbytes)

    logging.info(f"New master key generated for {obj.chain}! Fingerprint: {fingerprint}")

@cli.command(short_help='Generate a new address for chain and master key')
@click.option('-f', '--fingerprint', required=True,
                help='A 4B fingerprint that identifies the master key.')
@click.option('-p', '--path',
                help='The path of the address to derivate.')
@click.option('--hardened/--not-hardened', default=True,
                help='If the address must be derived using hardened path.')
@click.pass_obj
def new_address(obj, fingerprint, path, hardened):
    """Get new address for a said chain and masterkey.
    Each masterkey is identified through its fingerprint that have been returned when it was created.
    Return value is a new segwit native address, along with other information that might be necessary
    to import it as watch only:
    - the pubkey for Bitcoin and Elements address
    - the blinding private key for Elements address only
    """

    logging.info(f"Generating a new address for {obj.chain} and master key {fingerprint}.")

    address, pubkey, bkey = ssm.get_address_from_path(obj.chain, fingerprint, path, hardened)

    logging.info(f"New address for {obj.chain}: {address}, pubkey: {pubkey}, blinding key: {bkey}")

    return_value = {
        'address': address,
        'pubkey': pubkey,
        'blinding_key': bkey
    }

    click.echo(return_value)
