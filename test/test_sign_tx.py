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

CHAINS = ['bitcoin-regtest', 'elements-regtest']
# SIGN_VECTORS = path.join(path.dirname(path.realpath(__file__)), "sign_vectors.json")

ENTROPY = "91815eb893f3bc5b1798546b2519d0ac102b2563958c94fe863a65161e9098c5"
WIF_TEST = "cSTYZjZgieMXDM5rmw1o4P4d8kejMEHw8C9M3UZ1o7BgAV5dtLNo"
WIF_MAIN = "L26Z6pZqHafG3ucbPXCfh4ZZWXMKgnCF49zsw46WHzXfuk1K2ULr"
HDKEY_TEST = "tprv8ZgxMBicQKsPe8NFkADNQ7GMKyBkaWTRkrHStwdzcR9HvRbjbq6bNi37G3biAFtUE4hUmnuHojdqJdnqQ9qETcszgW41gn1e2GMjimt8HCQ"
HDKEY_MAIN = "xprv9s21ZrQH143K3K8j5bMsETeN1qmYLzRRRJNL2XDY8Sep8precTkqrxffLsS49tW9rdAhmhHXeP42qnF6GwVHeZcQ9rqi2RHb7AcKH5ohgCV"
FINGERPRINT = "a2ef94f8"

VECTORS = {
    "a2ef94f8": 
    [
        "tprv8ZgxMBicQKsPe8NFkADNQ7GMKyBkaWTRkrHStwdzcR9HvRbjbq6bNi37G3biAFtUE4hUmnuHojdqJdnqQ9qETcszgW41gn1e2GMjimt8HCQ",
        "0h/0h/270h",
        "",
        "0014ce903d07ab2d8d3f23bfbba65ca326cbf4b106fa",
        "1.00000000"
    ]
}

# our deposit to an address generated with our SSM
BTC_PREVTX = "d4c357ccf17cf4309b41fe18d777d7b5930f3f0f0525064435d3c9b76ba2d77d"
BTC_RAWTX = "02000000000101a289e4117137500b4badbadd9ea60d322fec4bc6dc460808ff7ab8ed5c42fa460000000000feffffff0200e1f50500000000160014ce903d07ab2d8d3f23bfbba65ca326cbf4b106fa7310102401000000160014ca072872ac9654716de7377edc727f2cc5997c800247304402205ecff480d22a816037a6105d35510d7e7d1bb217f9c12ce44c8052ad4e91861902202103c779953e2dfbbab39ce608bd73978433c5a89e86531517ce463fe5778bd1012103ea7057834d89ebf91b02d67725aa4ed7b5a418f75ee6aa8c06be54d3db083c1acb000000"
"""
{
  "txid": "d4c357ccf17cf4309b41fe18d777d7b5930f3f0f0525064435d3c9b76ba2d77d",
  "hash": "e056aaa234365fcf57a3b5044ae583be1105a5fadefa1dae621cf130ae59b342",
  "version": 2,
  "size": 222,
  "vsize": 141,
  "weight": 561,
  "locktime": 203,
  "vin": [
    {
      "txid": "46fa425cedb87aff080846dcc64bec2f320da69eddbaad4b0b50377111e489a2",
      "vout": 0,
      "scriptSig": {
        "asm": "",
        "hex": ""
      },
      "txinwitness": [
        "304402205ecff480d22a816037a6105d35510d7e7d1bb217f9c12ce44c8052ad4e91861902202103c779953e2dfbbab39ce608bd73978433c5a89e86531517ce463fe5778bd101",
        "03ea7057834d89ebf91b02d67725aa4ed7b5a418f75ee6aa8c06be54d3db083c1a"
      ],
      "sequence": 4294967294
    }
  ],
  "vout": [
    {
      "value": 1.00000000,
      "n": 0,
      "scriptPubKey": {
        "asm": "0 ce903d07ab2d8d3f23bfbba65ca326cbf4b106fa",
        "hex": "0014ce903d07ab2d8d3f23bfbba65ca326cbf4b106fa",
        "reqSigs": 1,
        "type": "witness_v0_keyhash",
        "addresses": [
          "bcrt1qe6gr6pat9kxn7galhwn9egexe06tzph6hycpvc"
        ]
      }
    },
    {
      "value": 48.99999859,
      "n": 1,
      "scriptPubKey": {
        "asm": "0 ca072872ac9654716de7377edc727f2cc5997c80",
        "hex": "0014ca072872ac9654716de7377edc727f2cc5997c80",
        "reqSigs": 1,
        "type": "witness_v0_keyhash",
        "addresses": [
          "bcrt1qegrjsu4vje28zm08xaldcunl9nzejlyqdfxsuq"
        ]
      }
    }
  ]
}
"""

# unsigned spending raw tx that we pass to our signing function
BTC_TXOUT = "02000000017dd7a26bb7c9d335440625050f3f0f93b5d777d718fe419b30f47cf1cc57c3d40000000000ffffffff01605af40500000000160014aa7e9c8bbf41d3bc16226551149aa598298f749d00000000"
# spending tx signed by Bitcoin/Elements, return value should be equal to this
SIGNED_TXID = "6c7980f9dbc4131ba38f51b0155a18e2f5f7e7e98f37e014010d05a60aada543"
SIGNED_TX = "020000000001017dd7a26bb7c9d335440625050f3f0f93b5d777d718fe419b30f47cf1cc57c3d40000000000ffffffff01605af40500000000160014aa7e9c8bbf41d3bc16226551149aa598298f749d02473044022053456f83819b446f189361801d2762b6fd32457a8ddffe762b3a0df07fa9c2de022015dcc3ada0b4cb6622663e5883720d3b622bd4ee26ca9f4c2f1bcdbbb4ddaa3001210358b092382102ea1beb1fcf60127f60e5efb67828a1688deb27bf077b8a1f3e7500000000"
"""
{
  "txid": "6c7980f9dbc4131ba38f51b0155a18e2f5f7e7e98f37e014010d05a60aada543",
  "hash": "7c205ad4e896ad092ce707a3d9988054aef4790b2c7860612be47f79b4d78bde",
  "version": 2,
  "size": 191,
  "vsize": 110,
  "weight": 437,
  "locktime": 0,
  "vin": [
    {
      "txid": "d4c357ccf17cf4309b41fe18d777d7b5930f3f0f0525064435d3c9b76ba2d77d",
      "vout": 0,
      "scriptSig": {
        "asm": "",
        "hex": ""
      },
      "txinwitness": [
        "3044022053456f83819b446f189361801d2762b6fd32457a8ddffe762b3a0df07fa9c2de022015dcc3ada0b4cb6622663e5883720d3b622bd4ee26ca9f4c2f1bcdbbb4ddaa3001",
        "0358b092382102ea1beb1fcf60127f60e5efb67828a1688deb27bf077b8a1f3e75"
      ],
      "sequence": 4294967295
    }
  ],
  "vout": [
    {
      "value": 0.99900000,
      "n": 0,
      "scriptPubKey": {
        "asm": "0 aa7e9c8bbf41d3bc16226551149aa598298f749d",
        "hex": "0014aa7e9c8bbf41d3bc16226551149aa598298f749d",
        "reqSigs": 1,
        "type": "witness_v0_keyhash",
        "addresses": [
          "bcrt1q4flfezalg8fmc93zv4g3fx49nq5c7aya0c3y6r"
        ]
      }
    }
  ]
}
"""

def test_sign_btc(sign_tx_btc_test_vectors, tmpdir):
    keys_dir = tmpdir.mkdir("ssm_keys")
    for k, v in sign_tx_btc_test_vectors.items():
        fingerprints = ""
        paths = ""
        values = ""
        for key in v["hdkeys"]:
          fingerprint = restore_hd_wallet(CHAINS[0], key, "", keys_dir)
          fingerprints = fingerprints + fingerprint
        for path in v["paths"]:
          paths = paths + path
        for value in v["values"]:
          values = values + value
          
        tx_out = sign_tx(CHAINS[0], v["prev_tx"][0], fingerprints, paths, values, keys_dir)
        assert tx_out == v["signed_tx"][0]


# TODO: test multiple inputs and elements transaction
