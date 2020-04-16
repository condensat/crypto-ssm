import sys
import json
import logging
import argparse

def main(args):
  logging.info("CryptoSSM start")
  args.func(args)

def genaddress(args):
  logging.info("CryptoSSM genaddress %d", args.id)
  print(json.dumps({
      "command": "genaddress",
      "id": args.id,
  }))

def signtx(args):
  logging.info("CryptoSSM signtx %s", args.tx)
  print(json.dumps({
      "command": "signtx",
      "tx": args.tx,
  }))

### ArgumentParser

parser = argparse.ArgumentParser(prog='ssm')
parser.add_argument(
    '-log',
    '--log',
    default='warning',
    help=(
        'Provide logging level.'
        'Example --log debug, default=warning'
    )
)
subparsers = parser.add_subparsers(help='sub-command help')

# command genaddress
parser_gen = subparsers.add_parser('genaddress', help='Generate new address for provided id')
parser_gen.set_defaults(func=genaddress)
parser_gen.add_argument(
    '-id',
    '--id',
    required=True,
    type=int,
    help=(
        'Related id'
    )
)

# command signtx
parser_sign = subparsers.add_parser('signtx', help='Sign the provided tx')
parser_sign.add_argument(
    '-tx',
    '--tx',
    required=True,
    help=(
        'Tx to sign'
    )
)
parser_sign.set_defaults(func=signtx)

args = parser.parse_args()
levels = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warn': logging.WARNING,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG
}
level = levels.get(args.log.lower())
if level is None:
    raise ValueError(
        f"log level given: {args.log}"
        f" -- must be one of: {' | '.join(levels.keys())}")

logging.basicConfig(level=level, stream=sys.stderr)

if __name__ == "__main__":
    main(args)
