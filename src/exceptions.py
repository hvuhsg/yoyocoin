from ecdsa import BadSignatureError

__all__ = ["ValidationError", "InsufficientBalanceError", "NonMatchingHash"]


class ValidationError(BadSignatureError):
    pass


class InsufficientBalanceError(ValidationError):
    pass


class NonMatchingHash(ValidationError):
    pass

