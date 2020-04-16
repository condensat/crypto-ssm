import sys
import logging
import argparse

def main(args):
  logging.info("CryptoSSM start")

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
