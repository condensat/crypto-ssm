# Crypto SSM Server

## Start server

```bash
  python server.py
```

## Call JsonRPC method

```bash
export SSM_ENDPOINT="http://localhost:5000/api/v1"
export MASTER_ENTROPY="9e8ff5dd31e53502cfcd06e568cbdc881d63e598f8d28e90d403b4c986cf1e60"

curl -i -X POST -H "Content-Type: application/json" -d '{
        "jsonrpc": "2.0",
        "method": "new_master",
        "params": ["bitcoin-main", "'"$MASTER_ENTROPY"'", true],
        "id": "42"
    }' $SSM_ENDPOINT
```

```bash
export SSM_ENDPOINT="http://localhost:5000/api/v1"
export KEY_FINGERPRINT="548041a6"

curl -i -X POST -H "Content-Type: application/json" -d '{
        "jsonrpc": "2.0",
        "method": "get_xpub",
        "params": ["bitcoin-main", "'"$KEY_FINGERPRINT"'"],
        "id": "42"
    }' $SSM_ENDPOINT
```

```bash
export SSM_ENDPOINT="http://localhost:5000/api/v1"
export KEY_FINGERPRINT="548041a6"

curl -i -X POST -H "Content-Type: application/json" -d '{
        "jsonrpc": "2.0",
        "method": "get_xprv",
        "params": ["bitcoin-main", "'"$KEY_FINGERPRINT"'"],
        "id": "42"
    }' $SSM_ENDPOINT
```

```bash
export SSM_ENDPOINT="http://localhost:5000/api/v1"
export KEY_FINGERPRINT="548041a6"
export HD_PATH="84'/0'/4'"

curl -i -X POST -H "Content-Type: application/json" -d '{
        "jsonrpc": "2.0",
        "method": "new_address",
        "params": ["bitcoin-main", "'"$KEY_FINGERPRINT"'", "'"$HD_PATH"'"],
        "id": "42"
    }' $SSM_ENDPOINT
```

```bash
export SSM_ENDPOINT="http://localhost:5000/api/v1"
export KEY_FINGERPRINTS="548041a6 548041a6"
export HD_PATHS="84'/0'/42' 84'/0'/1337'"
export PREV_TX="0200000002d12f2f94516b39ab1b34ddb7fd6908829bdeabb79527330a40f2be7da4b0c96e0000000000ffffffff20a553ed13610836fe66731baae865090a2922bdf7fc0e14d9e6bde7a696f0b60000000000ffffffff01c041c8170000000016001458f5399fb6f22cf28ab1294de806f6fc607a900800000000"
export SPEND_VALUES="1.50000000 2.50000000"

curl -i -X POST -H "Content-Type: application/json" -d '{
        "jsonrpc": "2.0",
        "method": "sign_tx",
        "params": ["bitcoin-main", "'"$PREV_TX"'", "'"$KEY_FINGERPRINTS"'", "'"$HD_PATHS"'", "'"$SPEND_VALUES"'"],
        "id": "42"
    }' $SSM_ENDPOINT
```
