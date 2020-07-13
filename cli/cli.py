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
    encode_payload,
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
@click.option('-e', '--entropy', required=True,
                help='Either a password or some entropy to use for seed generation.')
@click.option('--isbytes/--notbytes', default=False,
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

    click.echo(encode_payload(fingerprint))

    logging.info(f"New master key generated for {obj.chain}! Fingerprint: {fingerprint}")

@cli.command(short_help='Restore masterkey from base58 xprv')
@click.argument('hdkey')
@click.option('-b', '--blindingkey', default=None,
                help='A 64B hex encoded master blindingkey for Elements wallet.')
@click.pass_obj
def restore_master(obj, hdkey, blindingkey):
    """Save the master key provided in the ssm-keys dir.
    For debugging purpose, don't use this in production.
    """

    fingerprint = ssm.restore_hd_wallet(obj.chain, hdkey, blindingkey)

    click.echo(fingerprint)

@cli.command(short_help='Generate a new address for chain and master key')
@click.option('-f', '--fingerprint', required=True,
                help='A 4B fingerprint that identifies the master key.')
@click.option('-p', '--path', required=True,
                help='The path of the address to derivate.')
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

    logging.debug(return_value)

    click.echo(encode_payload(return_value))

@cli.command(short_help='Get the extended public key (xpub) that corresponds to some master key.')
@click.option('-f', '--fingerprint', required=True,
                help='A 4B fingerprint that identifies the master key.')
@click.pass_obj
def get_xpub(obj, fingerprint):
    """Get extended public key for a said chain and masterkey.
    Each masterkey is identified through its fingerprint that have been returned when it was created.
    Return value is the xpub that allows to derive all the public keys and address without knowledge
    of any private key.
    """
    #TODO: maybe we could take a path and return a derived xpub? Do we have a use case for that?

    logging.info(f"Getting the xpub for {obj.chain} and master key {fingerprint}.")

    xpub = ssm.get_xpub(obj.chain, fingerprint)

    logging.debug(f"{obj.chain} {fingerprint} masterkey's xpub is {xpub}")

    click.echo(encode_payload(xpub))

@cli.command(short_help='Sign all or some inputs of a serialized transaction.')
@click.argument('transaction')
@click.argument('fingerprints')
@click.argument('paths')
@click.argument('scriptpubkeys')
@click.argument('values')
@click.pass_obj
def sign_tx(obj, transaction, fingerprints, paths, scriptpubkeys, values):
    """Take an unsigned, complete transaction, and return it signed and ready for broadcast.
    For each fingerprint, we need one path, but a fingerprint can be repeated as many time as necessary.
    SSM will take the fingerprint and the paths in the provided order, derivate the private key and try
    to sign the outputs in the same order.
    If number of fingerprints/paths is less than number of inputs, it will sign all that it can and return the tx as it is.
    Fingerprints and paths must be space separated in a single string. 
    """

    #logging.info(f"Signing tx {get_txid(transaction)} for {obj.chain}.")

    signed_tx = ssm.sign_tx(obj.chain, transaction, fingerprints, paths, scriptpubkeys, values)

    logging.debug(f"signed tx is {signed_tx}")

    click.echo(encode_payload(signed_tx))

@cli.command(short_help='Get the extended private key (xprv) that corresponds to some master key.')
@click.option('-f', '--fingerprint', required=True,
                help='A 4B fingerprint that identifies the master key.')
@click.pass_obj
def get_xprv(obj, fingerprint):
    """Get extended private key for a said chain and masterkey.
    FOR DEBUGGING PURPOSE ONLY, TURN IT OFF IN PRODUCTION
    """

    xprv = ssm.get_xprv(obj.chain, fingerprint)

    click.echo(xprv)