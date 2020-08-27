import click
import json
import logging
import sys
from collections import namedtuple

import ssm.exceptions as exceptions
import ssm.core as ssm

from ssm.connect import (
    ConnCtx,
    BITCOIN_REGTEST_RPC_PORT,
    LIQUID_REGTEST_RPC_PORT
)

from ssm.util import (
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


ConnParams = namedtuple('ConnParams', ['chain', 'password'])


@click.group()
@click.option('-c', '--chain', default='bitcoin-main', type=click.Choice(CHAINS),
                help='Define the chain we\'re on out of a list (default = \'bitcoin-main\').')
@click.option('-p', '--password', default=None, 
                help='Key to unlock the private keys.')
@click.option('-v', '--verbose', count=True,
              help='Print more information, may be used multiple times.')
@click.version_option()
@click.pass_context
def cli(ctx, verbose, chain, password):
    """Crypto SSM Command-Line Interface
    """

    set_logging(verbose)

    logging.info(f"Working on {chain}")
    
    ctx.obj = ConnParams(chain, password)


@cli.command(short_help='Generate a new seed and master key for the chain')
@click.argument('entropy')
@click.option('--isbytes/--notbytes', default=False,
                help='If set, entropy is to be used directly and will not be hashed.')
@click.option('-s', '--size', type=click.Choice(['32', '64']), default='64',
                help='Size of the seed in bytes, for compatibility with other softwares.')
@click.pass_obj
def new_master(obj, entropy, isbytes, size):
    """Generate a new seed and the corresponding master key for BIP32 derivation.
    The new seed can use either a password and a salt, or some entropy (32B).
    At least one of 2 is required.
    Return value is the fingerprint of the new master key.
    """

    logging.info(f"Generating a new master key for {obj.chain}.")

    fingerprint = ssm.generate_new_hd_wallet(obj.chain, entropy, isbytes, size)

    click.echo(fingerprint)

    logging.info(f"New master key generated for {obj.chain}! Fingerprint: {fingerprint}")

@cli.command(short_help='Generate a new address for chain and master key')
@click.argument('fingerprint')
@click.argument('path')
@click.pass_obj
def new_address(obj, fingerprint, path):
    """Get new address for a said chain and masterkey.
    Each masterkey is identified through its fingerprint that have been returned when it was created.
    Return value is a new segwit native address, along with other information that might be necessary
    to import it as watch only:
    - the pubkey for Bitcoin and Elements address
    - the blinding private key for Elements address only
    """

    logging.info(f"Generating a new address for {obj.chain} and master key {fingerprint}.")

    address, pubkey, bkey = ssm.get_address_from_path(obj.chain, fingerprint, path)

    return_value = {
        'address': address,
        'pubkey': bytes(pubkey).hex()
    }

    if bkey is not None:
        return_value['blinding_key'] = bytes(bkey).hex()

    click.echo(json.dumps(return_value))

@cli.command(short_help='Get the extended public key (xpub) that corresponds to some master key.')
@click.argument('fingerprint')
@click.option('-p', '--path', default="root")
@click.pass_obj
def get_xpub(obj, fingerprint, path):
    """Get extended public key for a said chain and masterkey.
    Each masterkey is identified through its fingerprint that have been returned when it was created.
    Return value is the xpub that allows to derive all the public keys and address without knowledge
    of any private key.
    """
    #TODO: maybe we could take a path and return a derived xpub? Do we have a use case for that?

    logging.info(f"Getting the xpub for {obj.chain} and master key {fingerprint} on path {path}.")

    xpub = ssm.get_xpub(obj.chain, fingerprint, path)

    logging.debug(f"{obj.chain} {fingerprint} masterkey's xpub on {path} is {xpub}")

    click.echo(xpub)

@cli.command(short_help='Sign all or some inputs of a serialized transaction.')
@click.argument('transaction')
@click.argument('fingerprints')
@click.argument('paths')
@click.argument('values')
@click.pass_obj
def sign_tx(obj, transaction, fingerprints, paths, values):
    """Take an unsigned, complete transaction, and return it signed and ready for broadcast.
    For each fingerprint, we need one path, but a fingerprint can be repeated as many time as necessary.
    SSM will take the fingerprint and the paths in the provided order, derivate the private key and try
    to sign the outputs in the same order.
    If number of fingerprints/paths is less than number of inputs, it will sign all that it can and return the tx as it is.
    Fingerprints and paths must be space separated in a single string. 
    """

    #logging.info(f"Signing tx {get_txid(transaction)} for {obj.chain}.")

    signed_tx = ssm.sign_tx(obj.chain, transaction, fingerprints, paths, values)

    logging.debug(f"signed tx is {signed_tx}")

    click.echo(signed_tx)
