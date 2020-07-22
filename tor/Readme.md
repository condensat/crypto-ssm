# CryptoSSM tor hidden service

Docker stack for running crypto-ssm as a tor hidden service.
Dependencies: `docker` & `docker-compose`

## Build docker image

```bash
  make build && make publish
```

## Run crypto-ssm

```bash
  make start
```

## Tor Keys

Hidden service keys and hostname are stored in `ssm-service` directory.
