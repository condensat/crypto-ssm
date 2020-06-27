import wallycore as wally
import cli.exceptions as exceptions
import logging
from cli.util import (
    CHAINS,
    save_to_disk,
    retrieve_from_disk,
    harden_path
)

PREFIXES = {
    'bitcoin-main': 'bc',
    'bitcoin-test': 'tb',
    'bitcoin-regtest': 'bcrt',
    'liquidv1': 'ex',
    'elements-regtest': 'ert',
    'liquidv1-confidential': 'lq',
    'elements-regtest-confidential': 'el'
}

SALT_LEN = 32
HMAC_COST = 2048

def generate_entropy_from_password(password):
    """we can generate entropy from some password. The randomly generated salt also need to be saved.
    """
    # First make sure we know for which network we need a seed
    try:
        assert chain in CHAINS
    except AssertionError:
        raise exceptions.UnexpectedValueError("Unknown chain.")

    # Fail if password is None or empty
    if len(password) < 1:
        logging.error("You provided no password")
        raise exceptions.MissingValueError("Can't generate a new seed without password")
    elif len(password) < 16:
        logging.warning(f"Password provided is only {len(password)} characters long\n"
                            "That might be too short to be secure")

    _pass = password.encode('utf-8')
    logging.info(f"Generating salt of {SALT_LEN} bytes")
    salt = bytearray(urandom(SALT_LEN))
    logging.info(f"Salt is {salt}")
    # TODO: Save the salt on a file or db

    # Let's generate entropy from the provided password
    entropy = bytearray('0'.encode('utf-8') * 64)
    entropy = wally.pbkdf2_hmac_sha512(_pass, salt, 0, HMAC_COST)

    return entropy

def generate_mnemonic_from_entropy(entropy):
    """Generate a mnemonic of either 12 or 24 words.
    We can feed it the entropy we generated from a password or another way.
    We should generate 24 words if we want it to be compatible with Ledger
    """
    if len(entropy) not in [16, 32]:
        raise exceptions.UnexpectedValueError(f"Entropy is {len(entropy)}. "
                                                "It must be 16 or 32 bytes.")
    mnemonic = wally.bip39_mnemonic_from_bytes(None, entropy) # 1st argument is language, default is english
    logging.info(f"mnemonic generated from entropy.")
    return mnemonic

def generate_masterkey_from_mnemonic(mnenonic, chain):
    """Generate a masterkey pair + a master blinding key if chain is Elements.
    """
    if chain in ['bitcoin-main', 'liquidv1']:
        version = wally.BIP32_VER_MAIN_PRIVATE
    else:
        version = wally.BIP32_VER_TEST_PRIVATE
    
    # first get the seed from the mnemonic. We don't allow using a passphrase for now
    seed = bytearray(64) # seed is 64 bytes
    wally.bip39_mnemonic_to_seed(mnemonic, None, seed)

    # Now let's derivate the master privkey from seed
    master_key_private = wally.bip32_key_from_seed(seed, version, 0)
    fingerprint = wally.bip32_key_get_fingerprint(master_key_private)

    # dump the hdkey to disk. filename is key fingerprint
    #data = wally.bip32_key_serialize(master_key_private, wally.bip32_FLAG_KEY_PRIVATE)
    save_to_disk(master_key_private, fingerprint)

    # If chain is Elements, we can also derive the blinding key from the same seed
    if chain in ['liquidv1', 'elements-regtest']:
        master_blinding_key = bytearray(64)
        master_blinding_key = wally.asset_blinding_key_from_seed(seed) # SLIP-077 derivation

    # TODO: what if we lose the seed? 

    # We return the fingerprint only to the caller and keep the keys here
    return fingerprint

def get_address_from_path(chain, fingerprint, path, hardened=True):
    masterkey = retrieve_from_disk(fingerprint)
    if hardened == False:
        child = wally.bip32_key_from_parent_path(masterkey, path, wally.bip32_FLAG_KEY_PRIVATE)
    else:
        child = wally.bip32_key_from_parent_path(masterkey, harden_path(path), wally.bip32_FLAG_KEY_PRIVATE)

    # get a new segwit native address from the child
    address = wally.bip32_key_to_addr_segwit(child, prefix.get(chain), 0)

    return address

def generate_new_hd_wallet(chain, entropy, is_bytes):
    if is_bytes == True:
        mnemonic = generate_mnemonic_from_entropy(entropy)
    else:
        mnemonic = generate_mnemonic_from_entropy(generate_entropy_from_password(entropy))
    
    return generate_masterkey_from_mnemonic(mnemonic, chain)
