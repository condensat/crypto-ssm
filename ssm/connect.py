from ssm.rpc import RawProxy, JSONRPCError
from ssm.exceptions import SsmError


LIQUID_REGTEST_RPC_PORT = 7040
BITCOIN_REGTEST_RPC_PORT = 18443
CONNECTION_ERROR_MESSAGE = \
    'Unable to connect to Bitcoin/Elements Node. Are you sure you have started the ' \
    'node and the parameters are correct?'


class ConnectionError(ValueError):
    """Unable to connect to the Bitcoin/Elements node"""


class ConnCtx(object):
    """Connection context

    Usage:
    with ConnCtx(credentials, critical) as cc:
        connection = cc.connection
        # code using connection
    """

    def __init__(self, credentials, critical, start_over=False):
        self.credentials = credentials
        # function to prompt a critical message, e.g. popup or logs
        self.critical = critical
        self.start_over = start_over

    def __enter__(self):
        return self

    @property
    def connection(self):
        """Get a connection with the node
        """
        try:
            return RawProxy(**self.credentials)
        except Exception as e:
            raise ConnectionError('{}\n\n{}'.format(CONNECTION_ERROR_MESSAGE,
                                                    str(e)))

    def __exit__(self, typ, value, stacktrace):
        if not typ:
            pass
        elif issubclass(typ, JSONRPCError):
            self.critical(title='Elements Node Error',
                          message=value.error.get('message'),
                          start_over=self.start_over)
        elif issubclass(typ, SsmError):
            self.critical(title='SSM Error',
                          message=str(value),
                          start_over=self.start_over)
        elif issubclass(typ, Exception):
            self.critical(title='Error',
                          message=str(value),
                          start_over=self.start_over)

        return True
