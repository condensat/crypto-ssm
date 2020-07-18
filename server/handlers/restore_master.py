import api
import ssm.core as ssm

jsonrpc = api.jsonrpc()

@jsonrpc.method('restore_master')
def restore_master(chain: str, hdkey: str, blindingkey: str) -> dict:
  fingerprint = ssm.restore_hd_wallet(chain, hdkey, blindingkey)
  return {'chain': chain, 'fingerprint': fingerprint}
