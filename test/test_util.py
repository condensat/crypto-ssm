import pytest
from io import BytesIO

from cli.util import (
    hdkey_to_base58,
    get_masterkey_from_disk,
    harden,
    parse_path,
    save_masterkey_to_disk,
    get_number_inputs,
    read_varint,
)

VARINT = {
    "00": 0, 
    "01": 1,
    "fdffff": 65535,
    "feefefefef": 4025479151, 
    "ffced6056880ac8589": 9909516222599648974
}

TX = "01000000000101813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d1000000006b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff02a135ef01000000001976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac19430600"

def test_read_varint():
    for k, v in VARINT.items():
        res = read_varint(BytesIO(bytes.fromhex(k)))
        assert res == v

def test_get_number_inputs():
    inputs = get_number_inputs(TX)
    assert inputs == 1