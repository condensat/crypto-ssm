import logging
import pickle

from cli.exceptions import (
    UnexpectedValueError,
    UnsupportedLiquidVersionError,
    UnsupportedWalletVersionError,
    LockedWalletError,
    InvalidAddressError,
    OwnProposalError,
)


def btc2sat(btc):
    return round(btc * 10**8)


def sat2btc(sat):
    return round(sat * 10**-8, 8)


def values2btc(m):
    return {k: sat2btc(v) for k, v in m.items()}


def sort_dict(d):
    return {k: v for k, v in sorted(d.items())}


def is_mine(address, connection):
    if not connection.validateaddress(address)['isvalid']:
        raise InvalidAddressError('Invalid address: {}'.format(address))
    return connection.getaddressinfo(address)['ismine']


#def check_not_mine(address, connection):
#    """Raise an OwnProposalError if address is owned by the wallet
#    """
#    if is_mine(address, connection):
#        raise OwnProposalError(OWN_PROPOSAL_ERROR_MSG)


def check_wallet_unlocked(connection):
    """Raise error if wallet is locked
    """
    wallet_info = connection.getwalletinfo()
    if wallet_info.get('unlocked_until', 1) == 0:
        raise LockedWalletError('Wallet locked, please unlock it to proceed')


def check_network(expect_mainnet, expect_network, connection):
    """Raise error if expected network and node network mismatch
    """
    blockchain_info = connection.getblockchaininfo()
    is_bitcoin = blockchain_info.get('chain') in (['main', 'regtest'])
    is_mainnet = blockchain_info.get('chain') in (['liquidv1', 'main'])
    if is_mainnet != expect_mainnet:
        networks = ('regtest', 'mainnet')
        exp, found = networks if is_mainnet else reversed(networks)
        msg = 'Network mismatch: tool expecting {}, node using {}.'.format(
            exp, found)
        raise UnexpectedValueError(msg)
    if is_bitcoin != expect_network:
        networks = ('bitcoin', 'liquidv1')
        exp, found = networks if is_bitcoin else reversed(networks)
        msg = 'Network mismatch: tool expecting {}, node using {}.'.format(
            exp, found)
        raise UnexpectedValueError(msg)

def do_initial_checks(connection, expect_mainnet, expect_network):
    """Do initial checks
    """
    check_network(expect_mainnet, expect_network, connection)


def set_logging(verbose):
    """Set logging level
    """

    logging.basicConfig(format='liquidswap %(levelname)s %(message)s')
    if verbose == 1:
        logging.root.setLevel(logging.INFO)
    elif verbose > 1:
        logging.root.setLevel(logging.DEBUG)


def save_to_disk(data, file):
    with open(file, 'wb') as f:
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

def retrieve_from_disk(file):
    with open(file, 'rb') as f:
        data = pickle.load(f)
    return data