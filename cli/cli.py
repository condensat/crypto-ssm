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
@click.option('-c', '--chain', required=True, type=click.Choice(CHAINS),
                help='Define the chain we\'re on out of a list.')
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

    logging.info(f"Generating a new master key for {chain}.")

    fingerprint = ssm.generate_new_hd_wallet(obj.chain, entropy, isbytes)

    logging.info(f"New master key generated for {chain}! Fingerprint: {fingerprint}")

    # TODO: save the fingerprint on db

