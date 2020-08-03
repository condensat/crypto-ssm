import pytest
import json
from os import path

from wallycore import (
    bip32_key_get_fingerprint,
    bip32_key_from_base58,
    bip32_key_to_base58,
    tx_get_output_value,
    tx_from_hex,
    WALLY_TX_FLAG_USE_WITNESS,
    BIP32_FLAG_KEY_PRIVATE
)

from ssm.core import (
    get_child_from_path,
    sign_tx,
    restore_hd_wallet,
)

from ssm.util import (
    hdkey_to_base58,
    get_masterkey_from_disk,
    harden,
    parse_path,
    save_masterkey_to_disk,
)

import ssm.exceptions as exceptions

CHAINS = ['bitcoin-regtest', 'elements-regtest']
BTC_VECTORS = path.join(path.dirname(path.realpath(__file__)), "sign_tx_btc_test_vectors.json")
ELEMENTS_VECTORS = path.join(path.dirname(path.realpath(__file__)), "sign_tx_elements_test_vectors.json")
FALSE_VECTORS = path.join(path.dirname(path.realpath(__file__)), "sign_tx_false_test_vectors.json")

ENTROPY = "91815eb893f3bc5b1798546b2519d0ac102b2563958c94fe863a65161e9098c5"
WIF_TEST = "cSTYZjZgieMXDM5rmw1o4P4d8kejMEHw8C9M3UZ1o7BgAV5dtLNo"
#WIF_MAIN = "L26Z6pZqHafG3ucbPXCfh4ZZWXMKgnCF49zsw46WHzXfuk1K2ULr"
HDKEY_TEST = "tprv8ZgxMBicQKsPe8NFkADNQ7GMKyBkaWTRkrHStwdzcR9HvRbjbq6bNi37G3biAFtUE4hUmnuHojdqJdnqQ9qETcszgW41gn1e2GMjimt8HCQ"
#HDKEY_MAIN = "xprv9s21ZrQH143K3K8j5bMsETeN1qmYLzRRRJNL2XDY8Sep8precTkqrxffLsS49tW9rdAhmhHXeP42qnF6GwVHeZcQ9rqi2RHb7AcKH5ohgCV"
FINGERPRINT = "a2ef94f8"
BLINDING_KEY = "cf215ffecd670b7427b2fc90ee129ab6f801c1deed4a1b9b1b0341a8c05d8a43aafb994891a4d42e9afefd0614d497e65d572f939e04190659f93f5bad8d446e"

# our deposit to an address generated with our SSM
BTC_PREVTX = "d4c357ccf17cf4309b41fe18d777d7b5930f3f0f0525064435d3c9b76ba2d77d"
BTC_RAWTX = "02000000000101a289e4117137500b4badbadd9ea60d322fec4bc6dc460808ff7ab8ed5c42fa460000000000feffffff0200e1f50500000000160014ce903d07ab2d8d3f23bfbba65ca326cbf4b106fa7310102401000000160014ca072872ac9654716de7377edc727f2cc5997c800247304402205ecff480d22a816037a6105d35510d7e7d1bb217f9c12ce44c8052ad4e91861902202103c779953e2dfbbab39ce608bd73978433c5a89e86531517ce463fe5778bd1012103ea7057834d89ebf91b02d67725aa4ed7b5a418f75ee6aa8c06be54d3db083c1acb000000"

# unsigned spending raw tx that we pass to our signing function
BTC_TXOUT = "02000000017dd7a26bb7c9d335440625050f3f0f93b5d777d718fe419b30f47cf1cc57c3d40000000000ffffffff01605af40500000000160014aa7e9c8bbf41d3bc16226551149aa598298f749d00000000"
# spending tx signed by Bitcoin/Elements, return value should be equal to this
SIGNED_TXID = "6c7980f9dbc4131ba38f51b0155a18e2f5f7e7e98f37e014010d05a60aada543"
SIGNED_TX = "020000000001017dd7a26bb7c9d335440625050f3f0f93b5d777d718fe419b30f47cf1cc57c3d40000000000ffffffff01605af40500000000160014aa7e9c8bbf41d3bc16226551149aa598298f749d02473044022053456f83819b446f189361801d2762b6fd32457a8ddffe762b3a0df07fa9c2de022015dcc3ada0b4cb6622663e5883720d3b622bd4ee26ca9f4c2f1bcdbbb4ddaa3001210358b092382102ea1beb1fcf60127f60e5efb67828a1688deb27bf077b8a1f3e7500000000"

@pytest.fixture
def sign_tx_btc_test_vectors():
    with open(BTC_VECTORS) as f:
        return json.load(f)

@pytest.fixture
def sign_tx_elements_test_vectors():
    with open(ELEMENTS_VECTORS) as f:
        return json.load(f)

@pytest.fixture
def sign_tx_false_test_vectors():
    with open(FALSE_VECTORS) as f:
        return json.load(f)

def prepare_signature(chain:str, case: dict, keys_dir: str):
    fingerprints = ""
    paths = ""
    values = ""
    bkeys = []

    [bkeys.append(key) for key in case["master blinding key"]]
    for key in case["hdkeys"]:
      if bkeys[0]:
        bkey = bkeys.pop(0)
      else:
        bkey = ""
      fingerprint = restore_hd_wallet(chain, key, bkey, keys_dir)
      if not fingerprints:
        fingerprints = fingerprint
      else:
        fingerprints = fingerprints + " " + fingerprint
    for path in case["paths"]:
      if not paths:
        paths = path
      else:
        paths = paths + " " + path
    for value in case["values"]:
      if not values:
        values = value
      else:
        values = values + " " + value

    prev_tx = case["prev_tx"][0]

    return fingerprints, paths, values, prev_tx

def test_wrong_number_inputs(sign_tx_false_test_vectors, tmpdir):
    keys_dir = tmpdir.mkdir("ssm_keys")
    for k, v in sign_tx_false_test_vectors.items():
        if "wrong number" in k:
            fingerprints, paths, values, prev_tx = prepare_signature(CHAINS[0], v.copy(), keys_dir)
            with pytest.raises(exceptions.MissingValueError):
                sign_tx(CHAINS[0], prev_tx, fingerprints, paths, values, keys_dir)

def test_sign_btc(sign_tx_btc_test_vectors, tmpdir):
    keys_dir = tmpdir.mkdir("ssm_keys")
    for k, v in sign_tx_btc_test_vectors.items():
      for case in v:
        fingerprints, paths, values, prev_tx = prepare_signature(k, case.copy(), keys_dir)
        tx_out = sign_tx(k, prev_tx, fingerprints, paths, values, keys_dir)
        assert tx_out == case["signed_tx"][0]

def test_sign_elements(sign_tx_elements_test_vectors, tmpdir):
    keys_dir = tmpdir.mkdir("ssm_keys")
    for k, v in sign_tx_elements_test_vectors.items():
      for case in v:
        fingerprints, paths, values, prev_tx = prepare_signature(k, case.copy(), keys_dir)
        tx_out = sign_tx(k, prev_tx, fingerprints, paths, values, keys_dir)
        assert tx_out == case["signed_tx"][0]
