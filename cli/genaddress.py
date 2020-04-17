import logging
import json


def genaddress(args):
  logging.info("CryptoSSM genaddress %d", args.id)
  print(json.dumps({
      "command": "genaddress",
      "id": args.id,
  }))


if __name__ == "__main__":
  import logger
  logger.setup(logger.Args('debug'))

  from collections import namedtuple
  Args = namedtuple('Args', 'command id')
  genaddress(Args('genaddress', 42))
