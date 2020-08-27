import pytest
import json
from os import path

from wallycore import (
    bip32_key_get_fingerprint,
    bip32_key_from_base58,
)

from ssm.core import (
    generate_entropy_from_password,
    generate_mnemonic_from_entropy,
    generate_seed_from_mnemonic,
    generate_masterkey_from_mnemonic,
    generate_master_blinding_key_from_seed,
    generate_new_hd_wallet,    
)

from ssm.util import (
    hdkey_to_base58,
    get_masterkey_from_disk,
)

CHAIN = "bitcoin-main"
PASSPHRASE = "TREZOR"

# test vectors adapted from https://raw.githubusercontent.com/trezor/python-mnemonic/master/vectors.json
BIP39_VECTORS = path.join(path.dirname(path.realpath(__file__)), "bip39_test_vectors.json")

"""Example:
{
    "00000000000000000000000000000000": 
    [
        "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about",
        "c55257c360c07c72029aebc1b53c05ed0362ada38ead3e3e9efa3708e53495531f09a6987599d18264c1e1c92f2cf141630c7a3c4ab7c81b2f001698e7463b04",
        "xprv9s21ZrQH143K3h3fDYiay8mocZ3afhfULfb5GX8kCBdno77K4HiA15Tg23wpbeF1pLfs1c5SPmYHrEpTuuRhxMwvKDwqdKiGJS9XFKzUsAF"
    ],
    ...
}
"""

# test vectors from https://en.bitcoin.it/wiki/BIP_0032#Test_Vectors
SEED1 = "000102030405060708090a0b0c0d0e0f"
M_XPUB = "xpub661MyMwAqRbcFtXgS5sYJABqqG9YLmC4Q1Rdap9gSE8NqtwybGhePY2gZ29ESFjqJoCu1Rupje8YtGqsefD265TMg7usUDFdp6W1EGMcet8"
M_XPRIV = "xprv9s21ZrQH143K3QTDL4LXw2F7HEK3wJUD2nW2nRk4stbPy6cq3jPPqjiChkVvvNKmPGJxWUtg6LnF5kejMRNNU3TGtRBeJgk33yuGBxrMPHi"

@pytest.fixture
def bip39_test_vectors():
    with open(BIP39_VECTORS) as f:
        return json.load(f)

def test_bip39_entropy_to_mnemonic(bip39_test_vectors):
    for k, v in bip39_test_vectors.items():
        mnemomic = generate_mnemonic_from_entropy(bytes.fromhex(k))
        assert mnemomic == v[0]

def test_bip39_mnemonic_to_seed(bip39_test_vectors):
    for _, v in bip39_test_vectors.items():
        seed = generate_seed_from_mnemonic(v[0], PASSPHRASE)
        assert seed.hex() == v[1]

def test_bip39_seed_to_hdkey(bip39_test_vectors, tmpdir):
    keys_dir = tmpdir.mkdir("ssm_keys")
    size = '64'
    fingerprints = []
    xpriv = []
    for _, v in bip39_test_vectors.items():
        fingerprint = generate_masterkey_from_mnemonic(v[0], CHAIN, size, PASSPHRASE, keys_dir)
        xpriv.append(v[2])
        fingerprints.append(fingerprint)

    for i in range(0, len(fingerprints)):
        hdkey = get_masterkey_from_disk(CHAIN, fingerprints[i], False, keys_dir)
        assert hdkey_to_base58(hdkey) == xpriv[i]

#TODO: test the generation of 32B seed, maybe find a test set from Bitcoin Core?
        