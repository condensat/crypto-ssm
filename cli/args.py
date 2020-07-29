import argparse

import logger

from genaddress import genaddress
from signtx import signtx


def parse():
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
  subparsers = parser.add_subparsers(dest='command', help='sub-command help')

  # command genaddress
  parser_gen = subparsers.add_parser(
      'genaddress', help='Generate new address for provided id')
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

  # parse args
  args = parser.parse_args()

  if not hasattr(args, 'func'):
    raise Exception("sub-command not set")

  logger.setup(args)
  return args
