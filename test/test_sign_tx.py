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

from core.ssm import (
    get_child_from_path,
    sign_tx, 
)

from core.util import (
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

BTC_PREVTX = "ead83a99b5055fa2c225aab11b3b99c1207fb134c544ffd31f93d7a6a51d24cc"
BTC_RAWTX = "020000000001013cb016fe5676d8e8e30c5ef70098da6870cd44b7decbbd234d48f4e9b57728db0000000000feffffff0200e1f50500000000160014ce903d07ab2d8d3f23bfbba65ca326cbf4b106fafc05102401000000160014ca072872ac9654716de7377edc727f2cc5997c8002473044022039c8bb2116934d6701a6cb5a01befed791af048d33926a0193733499a3949a1f022008f953873d54365c5ca0725c09f12f6f7c19dc77ed9c7a222227d2ecd70beef8012103ea7057834d89ebf91b02d67725aa4ed7b5a418f75ee6aa8c06be54d3db083c1aca000000"
"""
{
  "txid": "ead83a99b5055fa2c225aab11b3b99c1207fb134c544ffd31f93d7a6a51d24cc",
  "hash": "e9efa1cb6464c6a29ea10eb41e622ea62a9de9f883378c05d3f3641c10e37ca6",
  "version": 2,
  "size": 222,
  "vsize": 141,
  "weight": 561,
  "locktime": 202,
  "vin": [
    {
      "txid": "db2877b5e9f4484d23bdcbdeb744cd7068da9800f75e0ce3e8d87656fe16b03c",
      "vout": 0,
      "scriptSig": {
        "asm": "",
        "hex": ""
      },
      "txinwitness": [
        "3044022039c8bb2116934d6701a6cb5a01befed791af048d33926a0193733499a3949a1f022008f953873d54365c5ca0725c09f12f6f7c19dc77ed9c7a222227d2ecd70beef801",
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
      "value": 48.99997180,
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

BTC_TXOUT = "02000000000101cc241da5a6d7931fd3ff44c534b17f20c1993b1bb1aa25c2a25f05b5993ad8ea0000000000ffffffff01c09ee60500000000160014fb4aa4cc31db90af4afb19fbbaedd38429634a800247304402205421766517c73075f9781224c654b4bb5c80080c73908371b9fa15b8f6d470e10220277101e5811da3492a264bb83e01cc6971c7e24c3bb9c7ad46675eb83d9eae6e01210358b092382102ea1beb1fcf60127f60e5efb67828a1688deb27bf077b8a1f3e7500000000"
SIGNED_TXID = "1ef17186cf43bedf27cea7827f2bbdfd7e5b3dbfc34c109fef21e2d2f3b9d4de"

def test_sign_btc(tmpdir):
    keys_dir = tmpdir.mkdir("ssm_keys")
    fingerprints = []
    paths = []
    values = []
    for k, v in VECTORS.items():
        masterkey = bip32_key_from_base58(v[0])
        fingerprints.append(k)
        paths.append(v[1])
        values.append(v[4])
        save_masterkey_to_disk(CHAINS[0], masterkey, k, False, keys_dir)

    TXOUT = sign_tx(CHAINS[0], BTC_TXOUT, fingerprints[0], paths[0], values[0], keys_dir)

    print(f"assert {TXOUT} == {BTC_TXOUT}")
    assert TXOUT == BTC_TXOUT


