import pytest
import json
from os import path

from wallycore import (
    bip32_key_get_fingerprint,
    bip32_key_from_base58,
    bip32_key_to_base58,
    BIP32_FLAG_KEY_PRIVATE
)

from core.ssm import (
    get_child_from_path,   
)

from core.util import (
    hdkey_to_base58,
    get_masterkey_from_disk,
    harden,
    parse_path,
    save_masterkey_to_disk,
)

CHAIN = "bitcoin-main"

BIP32_VECTORS = path.join(path.dirname(path.realpath(__file__)), "bip32_test_vectors.json")

"""Example:
{
    "xprv9s21ZrQH143K25QhxbucbDDuQ4naNntJRi4KUfWT7xo4EKsHt2QJDu7KXp1A3u7Bi1j8ph3EGsZ9Xvz9dGuVrtHHs7pXeTzjuxBrCmmhgC6":
    [
        "xprv9uPDJpEQgRQfDcW7BkF7eTya6RPxXeJCqCJGHuCJ4GiRVLzkTXBAJMu2qaMWPrS7AANYqdq6vcBcBUdJCVVFceUvJFjaPdGZ2y9WACViL4L",
        "xpub68NZiKmJWnxxS6aaHmn81bvJeTESw724CRDs6HbuccFQN9Ku14VQrADWgqbhhTHBaohPX4CjNLf9fq9MYo6oDaPPLPxSb7gwQN3ih19Zm4Y"
    ]
}
"""

@pytest.fixture
def bip32_test_vectors():
    with open(BIP32_VECTORS) as f:
        return json.load(f)

@pytest.fixture
def paths():
    paths = {
        'xprv9s21ZrQH143K3QTDL4LXw2F7HEK3wJUD2nW2nRk4stbPy6cq3jPPqjiChkVvvNKmPGJxWUtg6LnF5kejMRNNU3TGtRBeJgk33yuGBxrMPHi': [], 
        'xprv9s21ZrQH143K31xYSDQpPDxsXRTUcvj2iNHm5NUtrGiGG5e2DtALGdso3pGz6ssrdK4PFmM8NSpSBHNqPqm55Qn3LqFtT2emdEXVYsCzC2U': [], 
        'xprv9s21ZrQH143K25QhxbucbDDuQ4naNntJRi4KUfWT7xo4EKsHt2QJDu7KXp1A3u7Bi1j8ph3EGsZ9Xvz9dGuVrtHHs7pXeTzjuxBrCmmhgC6': []
    }
    paths['xprv9s21ZrQH143K3QTDL4LXw2F7HEK3wJUD2nW2nRk4stbPy6cq3jPPqjiChkVvvNKmPGJxWUtg6LnF5kejMRNNU3TGtRBeJgk33yuGBxrMPHi'] = [
        '0h', 
        '0h/1', 
        '0h/1/2h', 
        '0h/1/2h/2', 
        '0h/1/2h/2/1000000000'
    ]
    paths['xprv9s21ZrQH143K31xYSDQpPDxsXRTUcvj2iNHm5NUtrGiGG5e2DtALGdso3pGz6ssrdK4PFmM8NSpSBHNqPqm55Qn3LqFtT2emdEXVYsCzC2U'] = [
        '0', 
        '0/2147483647h', 
        '0/2147483647h/1', 
        '0/2147483647h/1/2147483646h', 
        '0/2147483647h/1/2147483646h/2'
    ]
    paths['xprv9s21ZrQH143K25QhxbucbDDuQ4naNntJRi4KUfWT7xo4EKsHt2QJDu7KXp1A3u7Bi1j8ph3EGsZ9Xvz9dGuVrtHHs7pXeTzjuxBrCmmhgC6'] = [
        '0h'
    ]
    return paths

@pytest.fixture
def get_masterkey_to_disk(tmpdir):
    with open(BIP32_VECTORS) as f:
        data = json.load(f)
    
    for k, v in data.items():
        masterkey = k

def test_bip32_hdkey_derivation(bip32_test_vectors, paths, tmpdir):
    keys_dir = tmpdir.mkdir("ssm_keys")
    fingerprints = {}

    # First save the masterkeys in test vector to disk and get their fingerprint
    # we'll need it to derivate the keys
    for k, v in bip32_test_vectors.items():
        masterkey = bip32_key_from_base58(k)
        fingerprint = bytearray(4)
        bip32_key_get_fingerprint(masterkey, fingerprint)
        fingerprints[k] = str(fingerprint.hex())
        save_masterkey_to_disk(CHAIN, masterkey, str(fingerprint.hex()), False, keys_dir)
    
    # Now loop again in the test vectors, derive a xprv with all the paths
    for k, v in bip32_test_vectors.items():
        childs = v.copy()
        for path in paths[k]:
            child = get_child_from_path(CHAIN, fingerprints[k], path, keys_dir)
            test_child = childs.pop(0)
            assert bip32_key_to_base58(child, BIP32_FLAG_KEY_PRIVATE) == test_child

# TODO: test the extended pubkey and bech32 address derivation 