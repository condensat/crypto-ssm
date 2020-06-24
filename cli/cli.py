import click
import json
import logging
import sys
from collections import namedtuple

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


@cli.command(short_help='Accept a swap')
@click.argument('payload', type=click.File('r'))
@click.option('-o', '--output', type=click.File('w'))
@click.option('-f', '--fee-rate', type=float, default=None,
              help='Fee rate in BTC/Kb, if not set, it will be determined by '
                   'the wallet.')
@click.pass_obj
def accept(obj, payload, output, fee_rate):
    """Accept a swap

    Fund and (partially) sign a proposed transaction.
    """

    with ConnCtx(obj.credentials, critical) as cc:
        connection = cc.connection
        do_initial_checks(connection, obj.is_mainnet)
        address = obj.address
        address_type = obj.address_type
        proposal = decode_payload(payload.read())

        check_wallet_unlocked(connection)
        check_not_mine(proposal['u_address_p'], connection)

        ret = swap.parse_proposed(
            *[proposal[k] for k in PROPOSED_KEYS],
            connection)
        accepted_swap = swap.accept(*ret, connection, fee_rate, address, address_type)
        encoded_payload = encode_payload(accepted_swap)
        click.echo(encoded_payload, file=output)


@cli.command(short_help='Finalize a swap')
@click.argument('payload', type=click.File('r'))
@click.option('--send', '-s', is_flag=True, help="Send the transaction.")
@click.pass_obj
def finalize(obj, payload, send):
    """Finalize a swap

    Sign the remaining inputs, print the transaction or broadcast it.
    """

    with ConnCtx(obj.credentials, critical) as cc:
        connection = cc.connection
        do_initial_checks(connection, obj.is_mainnet)
        proposal = decode_payload(payload.read())
        check_wallet_unlocked(connection)
        check_not_mine(proposal['u_address_r'], connection)

        (incomplete_tx, _, _, _, _, _, _) = swap.parse_accepted(
            *[proposal[k] for k in ACCEPTED_KEYS],
            connection)

        ret = swap.finalize(incomplete_tx, connection, broadcast=send)

        if send:
            d = {'broadcast': True, 'txid': ret}
        else:
            d = {'broadcast': False, 'transaction': ret}

        click.echo(json.dumps(d, indent=4))
