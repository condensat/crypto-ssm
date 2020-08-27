import api
import ssm.core as ssm

jsonrpc = api.jsonrpc()

@jsonrpc.method('new_address')
def new_address(chain: str, fingerprint: str, path: str) -> dict:
    address, pubkey, bkey = ssm.get_address_from_path(chain, fingerprint, path)
    if chain in ['bitcoin-main', 'bitcoin-test', 'bitcoin-regtest']:
        return {"chain": chain, "address": address, "pubkey": bytes(pubkey).hex()}
    else:
        return {
            "chain": chain, 
            "address": address, 
            "pubkey": bytes(pubkey).hex(), 
            "blinding_key": bytes(bkey).hex()
            }
