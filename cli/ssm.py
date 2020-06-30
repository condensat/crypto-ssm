import wallycore as wally
import cli.exceptions as exceptions
import logging
from os import urandom, path
from cli.util import (
    CHAINS,
    PREFIXES,
    CA_PREFIXES,
    save_to_disk,
    retrieve_from_disk,
    harden_path,
    bin_to_hex,
    check_dir,
    parse_path
)

SALT_LEN = 32
HMAC_COST = 2048
KEYS_DIR = "/ssm-keys"
BLINDING_KEYS_DIR = "blinding_keys"

def generate_entropy_from_password(password):
    """we can generate entropy from some password. The randomly generated salt also need to be saved.
    """
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
    logging.info(f"Salt is {bin_to_hex(salt)}")
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
    logging.debug(f"Mnenonic is {' '.join(mnemonic)}")
    return mnemonic

def generate_master_blinding_key_from_seed(seed, chain, fingerprint):
    """Generate the master blinding key from the seed, and save it to disk
    """
    master_blinding_key = bytearray(64)
    master_blinding_key = wally.asset_blinding_key_from_seed(seed) # SLIP-077 derivation

    # Save the blinding key to disk in a separate dir
    dir = path.join(KEYS_DIR, BLINDING_KEYS_DIR)
    check_dir(dir)
    filename = path.join(dir, fingerprint)
    save_to_disk(master_blinding_key, filename)

def get_blinding_key_from_address(address, chain, fingerprint):
    # First retrieve the master blinding key from disk
    dir = path.join(KEYS_DIR, BLINDING_KEYS_DIR)
    check_dir(dir)
    filename = path.join(dir, fingerprint)
    master_key = retrieve_from_disk(filename)
    # Next we compute the blinding keys for the address
    script_pubkey = wally.addr_segwit_to_bytes(address, PREFIXES.get(chain), 0)
    private_blinding_key = wally.asset_blinding_key_to_ec_private_key(master_key, script_pubkey)

    return private_blinding_key

def generate_masterkey_from_mnemonic(mnemonic, chain):
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
    fingerprint = bytearray(4)
    wally.bip32_key_get_fingerprint(master_key_private, fingerprint)

    # dump the hdkey to disk. Create a dir for each chain, filename is key fingerprint
    master_key_bin = wally.bip32_key_serialize(master_key_private, wally.BIP32_FLAG_KEY_PRIVATE)
    dir = path.join(KEYS_DIR, chain)
    check_dir(dir)
    filename = path.join(dir, str(bin_to_hex(fingerprint)))
    save_to_disk(master_key_bin, filename)

    # If chain is Elements, we can also derive the blinding key from the same seed
    if chain in ['liquidv1', 'elements-regtest']:
        generate_master_blinding_key_from_seed(seed, chain, str(fingerprint.hex()))

    # We return the fingerprint only to the caller and keep the keys here
    return str(bin_to_hex(fingerprint))

def get_address_from_path(chain, fingerprint, derivation_path, hardened=True):
    dir = path.join(KEYS_DIR, chain)
    check_dir(dir)
    filename = path.join(dir, fingerprint)
    master_key_bin = retrieve_from_disk(filename)
    masterkey = wally.bip32_key_unserialize(master_key_bin)
    lpath = parse_path(derivation_path)
    if hardened == False:
        child = wally.bip32_key_from_parent_path(masterkey, lpath, wally.BIP32_FLAG_KEY_PRIVATE)
    else:
        child = wally.bip32_key_from_parent_path(masterkey, harden_path(lpath), wally.BIP32_FLAG_KEY_PRIVATE)

    # get a new segwit native address from the child
    address = wally.bip32_key_to_addr_segwit(child, PREFIXES.get(chain), 0)

    # get the pubkey
    pubkey = wally.ec_public_key_from_private_key(wally.bip32_key_get_priv_key(child))
    
    # If Elements, get the blinding key, and create the corresponding confidential address
    if chain in ['liquidv1', 'elements-regtest']:
        blinding_privkey = get_blinding_key_from_address(address, chain, fingerprint)
        blinding_pubkey = wally.ec_public_key_from_private_key(blinding_privkey)
        address = wally.confidential_addr_from_addr_segwit(
                                                            address, 
                                                            PREFIXES.get(chain),
                                                            CA_PREFIXES.get(chain), 
                                                            blinding_pubkey
                                                        )
    else:
        blinding_privkey = None

    return address, pubkey, blinding_privkey

def generate_new_hd_wallet(chain, entropy, is_bytes):
    # First make sure we know for which network we need a seed
    try:
        assert chain in CHAINS
    except AssertionError:
        raise exceptions.UnexpectedValueError("Unknown chain.")

    # Check that the ssm-keys dir exists, create it if necessary
    check_dir(KEYS_DIR)

    if is_bytes == True:
        mnemonic = generate_mnemonic_from_entropy(entropy)
    else:
        mnemonic = generate_mnemonic_from_entropy(generate_entropy_from_password(entropy)[:32])
    
    return generate_masterkey_from_mnemonic(mnemonic, chain)

def get_xpub(chain, fingerprint):
    dir = path.join(KEYS_DIR, chain)
    check_dir(dir)
    filename = path.join(dir, fingerprint)
    master_key_bin = retrieve_from_disk(filename)
    masterkey = wally.bip32_key_unserialize(master_key_bin)
    # strip the xpriv to keep only the xpub
    # xpub = wally.bip32_key_strip_private_key(masterkey)
    # now return the xpub in its base58 readable format
    return wally.bip32_key_to_base58(masterkey, BIP32_FLAG_KEY_PUBLIC)
