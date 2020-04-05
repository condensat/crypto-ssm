import wallycore as wally
from os import urandom, path, remove
from rpc import RPCHost
from helper import wif, from_wif
import re

WIF_VERSION_MAINNET = int('80', 16)
WIF_VERSION_TESTNET = int('ef', 16)
WIF_FLAG_COMPRESSED = int('00', 16)
BIP32_VER_TEST_PRIVATE = int("04358394", 16)
BIP32_FLAG_KEY_PRIVATE = int('00', 16)

dir = path.expandvars('/home/$USER/liquid/')
dump_file1 = dir + 'test_dump'
dump_file2 = dir + 'test_dump2'
dump_file3 = dir + 'test_dump3'

# First erase any existing wallet dump
if path.isfile(dump_file1) is True:
    print("erasing previous test_dump")
    remove(dump_file1)

if path.isfile(dump_file2) is True:
    print("erasing previous test_dump2")
    remove(dump_file2)

if path.isfile(dump_file3) is True:
    print("erasing previous test_dump2")
    remove(dump_file3)

# This code is meant for demonstration only, please don't use this with real money

# Let's try using a privatekey generated by another Elements wallet as a seed
host_1 = RPCHost("http://user1:password1@127.0.0.1:18884")
host_2 = RPCHost("http://user1:password1@127.0.0.1:18885")
host_3 = RPCHost("http://user4:password4@127.0.0.1:18889")

address = host_1.call('getnewaddress')

wif_privkey = host_1.call('dumpprivkey', address)
print("wif from host1 is ", wif_privkey)

host_2.call('sethdseed', True, wif_privkey)
host_2.call('dumpwallet', dump_file2)

# Let's check the privkey labeled 'hdseed=1' in the dump, it should be the same
f = open(dump_file2)

for line in f:
    line = re.findall(".*" + wif_privkey + ".*", line)
    if line:
        print(line)
        break

# Now let's try with a random secret
entropy = bytearray(urandom(32))

wif_entropy = wally.wif_from_bytes(entropy, WIF_VERSION_TESTNET, WIF_FLAG_COMPRESSED)
print("wif from entropy is ", wif_entropy)

host_1.call('sethdseed', True, wif_entropy)
host_1.call('dumpwallet', dump_file1)

# Let's check the privkey labeled 'hdseed=1' in the dump, it should be the same
f = open(dump_file1)

for line in f:
    line = re.findall(".*" + wif_entropy + ".*", line)
    if line:
        print(line)
        break

# TODO: Let's use the same keys in the wallet of a third node and see if we have the same addresses

# Finally, let's create a master private key AND blinding key directly from the same seed in libwally
_pass = "password".encode('utf-8')
salt = "NaCl".encode('utf-8')
root = bytearray('0'.encode('utf-8') * 64)

wally.scrypt(_pass, salt, 1024, 8, 16, root)

mnemonic = wally.bip39_mnemonic_from_bytes(None, root[0:32])

seed = bytearray(64)
wally.bip39_mnemonic_to_seed(mnemonic, "", seed)

xpriv = wally.bip32_key_from_seed(seed, BIP32_VER_TEST_PRIVATE, 0)

print("the extended master privkey is ", wally.bip32_key_to_base58(xpriv, BIP32_FLAG_KEY_PRIVATE))

master_blinding_key = bytearray(64)
master_blinding_key = wally.asset_blinding_key_from_seed(root)

print("the master blinding key is ", master_blinding_key.hex())