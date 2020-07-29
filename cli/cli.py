import click
import json
import logging
import sys
from collections import namedtuple
import cli.exceptions

from cli.connect import (
    ConnCtx,
    BITCOIN_REGTEST_RPC_PORT,
    LIQUID_REGTEST_RPC_PORT
)

from cli.util import (
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


ConnParams = namedtuple('ConnParams', ['credentials', 'is_mainnet', 'is_bitcoin'])


@click.group()
@click.option('-u', '--service-url', default=None, type=str,
              help='Specify Bitcoin/Elements node URL for authentication.')
@click.option('-c', '--conf-file', default=None, type=str,
              help='Specify bitcoin.conf/elements.conf file for authentication.')
@click.option('-r', '--regtest', is_flag=True, help='Use with regtest.')
@click.option('-l', '--liquid', is_flag=True, help='Set network to Liquid (Elements),' 
                'or Bitcoin if false.')
@click.option('-v', '--verbose', count=True,
              help='Print more information, may be used multiple times.')
@click.version_option()
@click.pass_context
def cli(ctx, service_url, conf_file, regtest, verbose, liquid):
    """Crypto SSM Command-Line Interface
    """

    set_logging(verbose)

    is_mainnet = not regtest
    is_bitcoin = not liquid
    if not is_mainnet and is_bitcoin:
        service_port = BITCOIN_REGTEST_RPC_PORT
    elif not is_mainnet and not is_bitcoin:
        service_port = LIQUID_REGTEST_RPC_PORT
    elif is_mainnet:
        service_port = None
    credentials = {
        'conf_file': conf_file,
        'service_url': service_url,
        'service_port': service_port,
    }
    
    ctx.obj = ConnParams(credentials, is_mainnet, is_bitcoin)


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
