import api
import ssm.core as ssm

jsonrpc = api.jsonrpc()

@jsonrpc.method('new_master')
def new_master(chain: str, entropy: str, isbytes: bool) -> dict:
  fingerprint = ssm.generate_new_hd_wallet(chain, entropy, isbytes)
  return {'chain': chain, 'fingerprint': fingerprint}
