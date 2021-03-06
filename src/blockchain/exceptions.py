import ecdsa

__all__ = [
    "ValidationError",
    "InsufficientBalanceError",
    "NonMatchingHashError",
    "DuplicateNonceError",
    "NonLotteryMemberError",
    "WalletLotteryFreezeError",
    "GenesisIsNotValidError",
    "NonSequentialBlockIndexError",
]


class ValidationError(ecdsa.BadSignatureError):
    pass


class InsufficientBalanceError(ValidationError):
    pass


class NonMatchingHashError(ValidationError):
    pass


class DuplicateNonceError(ValidationError):
    pass


class NonLotteryMemberError(ValidationError):
    pass


class WalletLotteryFreezeError(ValidationError):
    pass


class GenesisIsNotValidError(ValidationError):
    pass


class NonSequentialBlockIndexError(ValidationError):
    pass
