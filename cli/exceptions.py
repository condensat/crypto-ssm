class SsmError(Exception):
    """Base class for all tool errors"""
    pass


class SameAssetError(SsmError):
    """Swap between the same asset are not supported"""


class InvalidAddressError(SsmError):
    """Found an invalid address"""


class OwnProposalError(SsmError):
    """Parsing your own proposal"""


class UnexpectedValueError(SsmError):
    """Found an unexpected value"""


class MissingValueError(SsmError):
    """An value the tool expects is missing"""


class FeeRateError(SsmError):
    """Invalid fee rate value"""


class UnblindError(SsmError):
    """Unable to fully unblind the transaction"""


class UnsignedTransactionError(SsmError):
    """Transaction is not fully signed"""


class InvalidTransactionError(SsmError):
    """Transaction won't be accepted by mempool"""


class UnsupportedLiquidVersionError(SsmError):
    """Liquid version running is below minimum supported"""


class UnsupportedWalletVersionError(SsmError):
    """Wallet version is below minimum supported"""


class LockedWalletError(SsmError):
    """Wallet is locked"""


class InvalidAssetIdError(SsmError):
    """Asset id or already in the wallet"""


class InvalidAssetLabelError(SsmError):
    """Asset label already set"""
