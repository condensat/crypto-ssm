import wallycore as wally
import logging
from os import urandom
import src.util as util

NETWORK = [
    'bitcoin-main',
    'bitcoin-reg',
    'elements-main',
    'elements-reg'    
]

# Generate a new master/blinding masterkeys pair, cf demo

class Wallet:
    def __init__(self, 
                password="", 
                salt="", 
                network='bitcoin-reg',
                mnemonic=False
                ):
        # First make sure we know for which network we need a seed
        try:
            assert network in NETWORK
        except AssertionError as e:
            logging.error(f"Please provide a network in {NETWORK}")
        self.network = network
        logging.info(f"Network is {self.network}")

        # Then we need to encode the password and salt strings
        if password == "" and salt == "":
            logging.warning(f"You provided no password nor salt")
        _pass = password.encode('utf-8')
        if salt == "":
            logging.warning(f"No salt given, generating one")
            salt = bytearray(urandom(32))
            logging.info(f"Salt is {salt}")
        else:
            salt = salt.encode('utf-8')

        # Let's call the entropy generated the seed
        seed = bytearray('0'.encode('utf-8') * 64)

        # Maybe the last difficulty parameter could be adjusted
        seed = wally.pbkdf2_hmac_sha512(_pass, salt, 0, 1024)

        # Generate the masterkeys with the same seed.
        # Maybe we don't need the mnemonics I guess it all depends 
        # if we'd rather store the password and salt or mnemonic words.
        # Anyway it's optional for now
        if mnemonic == True:
            mnemonic = wally.bip39_mnemonic_from_bytes(None, seed)
            logging.info(f"mnemonic is {mnemonic}")
        # Interesting to note that we're not BIP39 compliant,
        # might not be an issue though

        # The terminology is confusing, I propose the following:
        # hd_privkey and hd_pubkey are for the first key 
        # (directly parsed from the seed entropy)
        hd_privkey = wally.bip32_key_from_seed(seed, util.BIP32_VER_TEST_PRIVATE, 0)
        master_blinding_key = bytearray(64)
        master_blinding_key = wally.asset_blinding_key_from_seed(seed)
        
        self.hd_privkey = hd_privkey
        self.master_blinding_key = master_blinding_key

        logging.info(f"The generated hdkey is {wally.bip32_key_to_base58(hd_privkey, util.BIP32_FLAG_KEY_PRIVATE)}")
        logging.info(f"The generated master blinding key is {master_blinding_key}")

        # Here we use the very simple SLIP-0077 implementation in Libwally
        # Maybe we will need to add more levels of derivation at some point



# Derivate 2 keypairs, one for the transaction, one for its binding