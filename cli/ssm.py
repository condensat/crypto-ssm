import sys
import logging

import args


def main():
  try:
    options = args.parse()
    options.func(options)

  except Exception as e:
    logging.error("CryptoSSM error: %s" % e)
  except BaseException as e:
    logging.error("CryptoSSM system error: %s" % e)


if __name__ == "__main__":
  main()
