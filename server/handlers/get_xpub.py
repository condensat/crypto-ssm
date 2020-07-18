import api
import ssm.core as ssm

jsonrpc = api.jsonrpc()

@jsonrpc.method('get_xpub')
def get_xpub(chain, fingerprint: str) -> dict:
    xpub = ssm.get_xpub(chain, fingerprint)
    return {'chain': chain, "xpub": xpub}
