import api
import ssm.core as ssm

jsonrpc = api.jsonrpc()

@jsonrpc.method('get_xprv')
def get_xprv(chain: str, fingerprint: str) -> dict:
    xprv = ssm.get_xprv(chain, fingerprint)
    return {'chain': chain, "xprv": xprv}
