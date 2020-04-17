import sys
import logging

from collections import namedtuple
Args = namedtuple('Args', 'log')


def setup(args):
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
