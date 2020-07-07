import logging, json
from binascii import hexlify, unhexlify
from os import path, mkdir
from wallycore import (
    sha256d,
    bip32_key_unserialize,
    bip32_key_serialize,
    bip32_key_to_base58,
    BIP32_FLAG_KEY_PRIVATE,
    BIP32_FLAG_KEY_PUBLIC,
)

from cli.exceptions import (
    UnexpectedValueError,
    UnsupportedLiquidVersionError,
    UnsupportedWalletVersionError,
    LockedWalletError,
    InvalidAddressError,
    OwnProposalError,
)

CHAINS = [
    'bitcoin-main', 
    'bitcoin-test', 
    'bitcoin-regtest', 
    'liquidv1', 
    'elements-regtest',
]

CA_PREFIXES = {
    'liquidv1': 'lq',
    'elements-regtest': 'el'
}

PREFIXES = { 
    'bitcoin-main': 'bc', 
    'bitcoin-test': 'tb', 
    'bitcoin-regtest': 'bcrt',
    'liquidv1': 'ex',
    'elements-regtest': 'ert',
}

KEYS_DIR = "/ssm-keys"
BLINDING_KEYS_DIR = "blinding_keys"

INITIAL_HARDENED_INDEX = pow(2, 31)

def btc2sat(btc):
    return round(btc * 10**8)


def sat2btc(sat):
    return round(sat * 10**-8, 8)


def values2btc(m):
    return {k: sat2btc(v) for k, v in m.items()}


def sort_dict(d):
    return {k: v for k, v in sorted(d.items())}

def hdkey_to_base58(hdkey, private=True):
    return bip32_key_to_base58(hdkey, BIP32_FLAG_KEY_PRIVATE if private == True else BIP32_FLAG_KEY_PUBLIC)

def is_mine(address, connection):
    if not connection.validateaddress(address)['isvalid']:
        raise InvalidAddressError('Invalid address: {}'.format(address))
    return connection.getaddressinfo(address)['ismine']


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

    logging.basicConfig(format='SSM %(levelname)s %(message)s')
    if verbose == 1:
        logging.root.setLevel(logging.INFO)
    elif verbose > 1:
        logging.root.setLevel(logging.DEBUG)

def harden(idx):
    if idx[-1] is '\'' or idx[-1] is 'h':
        try:
            int(idx[:-1])
        except ValueError as e:
            print(e.args)
        idx = idx[:-1]
        if int(idx) >= INITIAL_HARDENED_INDEX:
            raise UnexpectedValueError("Can't harden an index greater than 2^31 - 1")
        return int(idx) + INITIAL_HARDENED_INDEX
    else:
        try:
            return int(idx)
        except ValueError as e:
            print(e.args)

def save_to_disk(data, file):
    with open(file, 'wb') as f:
        f.write(data)

def retrieve_from_disk(file):
    with open(file, 'rb') as f:
        data = f.read()
    return data

def bin_to_hex(bin):
    return bin.hex()

def check_dir(keys_dir):
    if path.isdir(keys_dir) == False:
        rights = 0o600
        try:
            mkdir(keys_dir, rights)
        except OSError:
            print(f"Can't create {keys_dir}")
    return True

def parse_path(path):
    lpath = []
    if path.find('/') >= 0:
        strpath = path.split('/')
        for idx in strpath:
            lpath.append(harden(idx))
    else:
        lpath.append(harden(path))
    return lpath

def encode_payload(data):
    json_data = json.dumps(data)
    data_bytes = bytes(json_data, 'utf-8')
    data_hex = data_bytes.hex()

    return data_hex

def get_txid(tx):
    "Return the double sha256 hash of the tx"
    return sha256d(tx)

def get_masterkey_from_disk(chain, fingerprint, blindingkey=False, dir=KEYS_DIR):
    if blindingkey:
        dir = path.join(dir, BLINDING_KEYS_DIR)
    else:
        dir = path.join(dir, chain)
    check_dir(dir)
    filename = path.join(dir, fingerprint)
    masterkey_bin = retrieve_from_disk(filename)
    if blindingkey:
        return masterkey_bin
    else:
        return bip32_key_unserialize(masterkey_bin)

def save_masterkey_to_disk(chain, masterkey, fingerprint, blindingkey=False, dir=KEYS_DIR):
    if blindingkey:
        dir = path.join(dir, BLINDING_KEYS_DIR)
        masterkey_bin = masterkey
    else:
        dir = path.join(dir, chain)
        masterkey_bin = bip32_key_serialize(masterkey, BIP32_FLAG_KEY_PRIVATE)
    check_dir(dir)
    # TODO: check that a file with the same fingerprint doesn't exist. 
    # The probability to have a collision on a fingerprint is small, but still
    filename = path.join(dir, fingerprint)
    save_to_disk(masterkey_bin, filename)

def save_salt_to_disk(fingerprint, salt):
    dir = path.join(KEYS_DIR, 'salt')
    check_dir(dir)
    filename = path.join(dir, fingerprint)
    save_to_disk(salt, filename)