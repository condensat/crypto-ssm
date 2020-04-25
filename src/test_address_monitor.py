import address_monitor as a_mon
import redis

host='127.0.0.1'
port=6379
db=0

r = redis.Redis(host, port, db)

scriptpubkey_legacy="76a914e241d530a4cec1e8156553c82bb729b8cae9620a88ac"
scriptpubkey_bech32="001419c390f8676efecf221341c239ca34758544923e"
scriptpubkey_p2shsegwit="a914374fba765d7331016c332b3802806215d8294eb587"
fake_legacy="77a914e241d530a4cec1e8156553c82bb729b8cae9620a88ac"
fake_bech32="011419c390f8676efecf221341c239ca34758544923e"
fake_p2shsegwit="a916374fba765d7331016c332b3802806215d8294eb587"
try:
    a_mon.add_address_to_monitor(r, scriptpubkey_legacy)
    a_mon.add_address_to_monitor(r, scriptpubkey_p2shsegwit)
    a_mon.add_address_to_monitor(r, scriptpubkey_bech32)
except:
    print("something's wrong with add_address")
# TODO write test for fake script
for k, v in a_mon.addr_type.items():
    print(r.smembers(v))
print(a_mon.rm_address(r, scriptpubkey_legacy))
print(a_mon.rm_address(r, scriptpubkey_p2shsegwit))
print(a_mon.rm_address(r, scriptpubkey_bech32))
