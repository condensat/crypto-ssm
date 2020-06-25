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
    do_initial_checks,
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


@cli.command(short_help='Get block height')
@click.pass_obj
def getblockcount(obj):
    """Get the current block height
    """

    with ConnCtx(obj.credentials, critical) as cc:
        connection = cc.connection
        do_initial_checks(connection, obj.is_mainnet, obj.is_bitcoin)

        blockcount = connection.getblockcount()
        click.echo(blockcount)


@cli.command(short_help='Import a watch-only address in a Bitcoin/Elements node')
@click.argument('address')
@click.argument('pubkey')
@click.argument('blindingkey')
@click.pass_obj
def importAddress(obj, address, pubkey, blindingkey=None):
    with ConnCtx(obj.credentials, critical) as cc:
        connection = cc.connection
        do_initial_checks(connection, obj.is_mainnet, obj.is_bitcoin)

        if obj.is_bitcoin == False and blindingkey == None:
            raise exceptions.UnexpectedValueError("Please provide a blindingkey for importing Elements address")  

        if connection.getaddressinfo(address).get("ismine") == True:
            raise exceptions.UnexpectedValueError("Can't import own address")
        
        if connection.getaddressinfo(address).get("iswatchonly") == True:
            raise exceptions.UnexpectedValueError("This address is already watched")

        if obj.is_bitcoin == True:
            # importaddress
            connection.importaddress(address)
            # importpubkey
            connection.importpubkey(pubkey)

        if obj.is_bitcoin == False:
            # importaddress
            connection.importaddress(address)
            # importpubkey
            connection.importpubkey(pubkey)
            # importblindingkey
            connection.importblindingkey(address, blindingkey)
            
        if connection.getaddressinfo(address).get("iswatchonly") == False:
            raise exceptions.Importfailed("the address couldn't be imported as watch-only")
