import wallycore as wally
import cli.exceptions as exceptions
import logging
from os import urandom, path
from cli.util import (
    CHAINS,
    PREFIXES,
    CA_PREFIXES,
    KEYS_DIR,
    BLINDING_KEYS_DIR,
    save_masterkey_to_disk,
    save_salt_to_disk,
    get_masterkey_from_disk,
    harden_path,
    bin_to_hex,
    check_dir,
    parse_path,
    hdkey_to_base58
)

SALT_LEN = 32
HMAC_COST = 2048

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
    logging.debug(f"Salt is {bin_to_hex(salt)}")

    # Let's generate entropy from the provided password
    entropy = bytearray('0'.encode('utf-8') * 64)
    entropy = wally.pbkdf2_hmac_sha512(_pass, salt, 0, HMAC_COST)

    return entropy, salt

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
    save_masterkey_to_disk(chain, master_blinding_key, fingerprint, True)

def generate_seed_from_mnemonic(mnemonic, passphrase=None):
    seed = bytearray(64) # seed is 64 bytes
    wally.bip39_mnemonic_to_seed(mnemonic, passphrase, seed)
    return seed

def get_blinding_key_from_address(address, chain, fingerprint):
    # First retrieve the master blinding key from disk
    master_key = get_masterkey_from_disk(chain, fingerprint, True)
    # Next we compute the blinding keys for the address
    script_pubkey = wally.addr_segwit_to_bytes(address, PREFIXES.get(chain), 0)
    private_blinding_key = wally.asset_blinding_key_to_ec_private_key(master_key, script_pubkey)

    return private_blinding_key

def generate_masterkey_from_mnemonic(mnemonic, chain, passphrase=None):
    """Generate a masterkey pair + a master blinding key if chain is Elements.
    """
    if chain in ['bitcoin-main', 'liquidv1']:
        version = wally.BIP32_VER_MAIN_PRIVATE
    else:
        version = wally.BIP32_VER_TEST_PRIVATE
    
    # first get the seed from the mnemonic. We don't allow using a passphrase for now
    seed = generate_seed_from_mnemonic(mnemonic)

    # Now let's derivate the master privkey from seed
    master_key = wally.bip32_key_from_seed(seed, version, 0)
    fingerprint = bytearray(4)
    wally.bip32_key_get_fingerprint(master_key, fingerprint)

    # dump the hdkey to disk. Create a dir for each chain, filename is key fingerprint
    master_key_bin = wally.bip32_key_serialize(master_key, wally.BIP32_FLAG_KEY_PRIVATE)
    save_masterkey_to_disk(chain, master_key_bin, str(fingerprint.hex()))

    # If chain is Elements, we can also derive the blinding key from the same seed
    if chain in ['liquidv1', 'elements-regtest']:
        generate_master_blinding_key_from_seed(seed, chain, str(fingerprint.hex()))

    # We return the fingerprint only to the caller and keep the keys here
    return str(bin_to_hex(fingerprint))

def get_child_from_path(chain, fingerprint, derivation_path, hardened=True):
    master_key_bin = get_masterkey_from_disk(chain, fingerprint)
    masterkey = wally.bip32_key_unserialize(master_key_bin)
    lpath = parse_path(derivation_path)
    if hardened == False:
        return wally.bip32_key_from_parent_path(masterkey, lpath, wally.BIP32_FLAG_KEY_PRIVATE)
    else:
        return wally.bip32_key_from_parent_path(masterkey, harden_path(lpath), wally.BIP32_FLAG_KEY_PRIVATE)


def get_address_from_path(chain, fingerprint, derivation_path, hardened=True):
    # get the child extended key
    child = get_child_from_path(chain, fingerprint, derivation_path, hardened)
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
        # This can be useful for testing, but it is not recommended for production since the 
        # entropy that is passed in argument is not salted
        mnemonic = generate_mnemonic_from_entropy(bytes.fromhex(entropy))
        salt = None
    else:
        stretched_key, salt = generate_entropy_from_password(entropy)
        mnemonic = generate_mnemonic_from_entropy(stretched_key[:32])
    
    fingerprint = generate_masterkey_from_mnemonic(mnemonic, chain)

    if salt:
        # We now save the salt in a file under the fingerprint name
        save_salt_to_disk(fingerprint, salt)

    return fingerprint

def get_xpub(chain, fingerprint):
    master_key_bin = get_masterkey_from_disk(chain, fingerprint)
    masterkey = wally.bip32_key_unserialize(master_key_bin)
    # now return the xpub in its base58 readable format
    return hdkey_to_base58(masterkey, False)

def sign_tx(chain, tx, fingerprints, paths, hardened=True):
    # first extract the fingerprints and paths in lists
    fingerprints = fingerprints.split()
    paths = paths.split()
    # Check if we have the same number of fingerprints and paths
    try:
        assert len(fingerprints) == len(paths)
    except:
        raise exceptions.MissingValueError("As many fingerprints as paths must be provided.")

    # Get a tx object from the tx_hex
    if chain in ['bitcoin-main', 'bitcoin-test', 'bitcoin-regtest']: 
        Tx = wally.tx_from_hex(tx, wally.WALLY_TX_FLAG_USE_WITNESS) 
    else: 
        Tx = wally.tx_from_hex(tx, wally.WALLY_TX_FLAG_USE_WITNESS | wally.WALLY_TX_FLAG_USE_ELEMENTS)
           
    print(f"fingerprints is {fingerprints}")
    print(f"paths is {paths}")
    # Now we loop on each fingerprint provided, compute the sighash and sign the same index input
    for i, f in enumerate(fingerprints):
        child = get_child_from_path(chain, fingerprints[i], paths[i], hardened)
        privkey = wally.bip32_key_get_priv_key(child)
        pubkey = wally.ec_public_key_from_private_key(privkey)
        hashToSign = wally.tx_get_elements_signature_hash(Tx, i, 
            bytearray([0x0, 0x14]) + wally.hash160(pubkey), 
            wally.tx_get_output_value(Tx, 0), 
            wally.WALLY_SIGHASH_ALL, 
            wally.WALLY_TX_FLAG_USE_WITNESS)
        sig = wally.ec_sig_from_bytes(privkey, hashToSign, wally.EC_FLAG_ECDSA | wally.EC_FLAG_GRIND_R)
        sig = wally.ec_sig_to_der(sig) + bytearray([wally.WALLY_SIGHASH_ALL])
        witnessStack = wally.tx_witness_stack_init(2)
        wally.tx_witness_stack_add(witnessStack, sig)
        wally.tx_witness_stack_add(witnessStack, pubkey)
        wally.tx_set_input_witness(Tx, i, witnessStack)

    # Now return the hex of the signed tx
    if chain in ['bitcoin-main', 'bitcoin-test', 'bitcoin-regtest']: 
        return wally.tx_to_hex(Tx, wally.WALLY_TX_FLAG_USE_WITNESS) 
    else: 
        return wally.tx_to_hex(Tx, wally.WALLY_TX_FLAG_USE_WITNESS & wally.WALLY_TX_FLAG_USE_ELEMENTS)