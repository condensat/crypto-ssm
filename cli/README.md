# Software Security Module command line

## Setup

- python3
- wallycore

## Main program

Main program can run each sub-command with log level.

- Stderr is used for logging.
- Stdout is used for print result in json

```bash
  python ssm.py --log=debug genaddress --id=42
```

```bash
  python ssm.py --log=debug signtx --tx=txid
```

## Sub-commands

Each sub-command can run separately for development:

```bash
  python genaddress.py
```

```bash
  python signtx.py
```