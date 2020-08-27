import api
import ssm.core as ssm

jsonrpc = api.jsonrpc()

@jsonrpc.method('new_master')
def new_master(chain: str, entropy: str, isbytes: bool, size="64") -> dict:
  fingerprint = ssm.generate_new_hd_wallet(chain, entropy, isbytes, size)
  return {'chain': chain, 'fingerprint': fingerprint}
