from ecdsa import BadSignatureError

__all__ = [
    "ValidationError",
    "InsufficientBalanceError",
    "NonMatchingHash",
    "DuplicateNonce",
    "NonLotteryMember",
    "WalletLotteryFreeze",
]


class ValidationError(BadSignatureError):
    pass


class InsufficientBalanceError(ValidationError):
    pass


class NonMatchingHash(ValidationError):
    pass


class DuplicateNonce(ValidationError):
    pass


class NonLotteryMember(ValidationError):
    pass


class WalletLotteryFreeze(ValidationError):
    pass
