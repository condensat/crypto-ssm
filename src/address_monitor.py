import redis

host='127.0.0.1'
port=6379
db=0

addr_type={
        '76a9': "legacy",
        'a914': "p2sh-segwit",
        '0014': "bech32"
        }

# initiate a new database
# update database with new address to monitor
## we'd better add the scriptPubkey than the address, as it is what will show up in the rawtx
## we can get it with the `getaddressinfo` rpc command
def add_address_to_monitor(r, scriptPubkey):
    try:
        isinstance(scriptPubkey, str)
        scriptPubkey[0:4] in addr_type
    except:
        raise ValueError("scriptPubkey value looks wrong")
    r.sadd(addr_type[scriptPubkey[0:4]], scriptPubkey)
    return r.sismember(addr_type[scriptPubkey[0:4]], scriptPubkey)

# remove one address, when we found it in the zmq queue
def rm_address(r, scriptPubkey):
    try:
        isinstance(scriptPubkey, str)
        scriptPubkey[0:4] in addr_type
    except:
        raise ValueError("scriptPubkey value looks wrong")
    try:
        r.sismember(addr_type[scriptPubkey[0:4]], scriptPubkey)
    except:
        raise ValueError("scripPubkey not in databse, can't delete")
    r.srem(addr_type[scriptPubkey[0:4]], scriptPubkey)
    return not r.sismember(addr_type[scriptPubkey[0:4]], scriptPubkey)

# look up for an address in the zmq published txs
## if an address is found in db, send the tx id to the client, and delete the address
## if no match, nothing happens
