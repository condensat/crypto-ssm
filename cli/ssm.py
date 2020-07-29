import sys
import logging
import signal

import args


def main():
  try:
    options = args.parse()
    options.func(options)

  except Exception as e:
    logging.error("CryptoSSM error: %s" % e)

  except SystemExit as e:
    logging.warning("CryptoSSM SystemExit, code: %s", e)
  except BaseException as e:
    logging.error("CryptoSSM system error: %s" % e)

def terminate(signum, frame):
   sys.exit(0)

if __name__ == "__main__":
  signal.signal(signal.SIGINT, terminate) # for ctrl-c shell+docker
  signal.signal(signal.SIGTERM, terminate)  # for docker stop

  main()
