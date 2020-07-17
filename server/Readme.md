# Crypto SSM Server

## Start server

```bash
  python server.py
```

## Call JsonRPC method

```bash
curl -i -X POST -H "Content-Type: application/json" -d '{
        "jsonrpc": "2.0",
        "method": "new_master",
        "params": ["foo"],
        "id": "42"
    }' http://localhost:5000/api/v1
```
