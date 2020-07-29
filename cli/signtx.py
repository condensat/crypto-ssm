import logging
import json


def signtx(args):
  logging.info("CryptoSSM signtx %s", args.tx)
  print(json.dumps({
      "command": args.command,
      "tx": args.tx,
  }))


if __name__ == "__main__":
  import logger
  logger.setup(logger.Args('debug'))

  from collections import namedtuple
  Args = namedtuple('Args', 'command tx')
  signtx(Args('signtx', 'foo'))
