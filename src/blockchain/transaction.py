import hashlib
from base64 import b64encode, b64decode
import ecdsa

from config import Config
from .exceptions import ValidationError, InsufficientBalanceError, DuplicateNonceError


class Transaction:
    def __init__(
        self, sender, recipient, amount, nonce: int, fee=None, signature=None, **kwargs
    ):
        if fee is None:
            fee = 1
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.fee = fee
        self.nonce = nonce
        self.signature = signature

    def to_dict(self):
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "fee": self.fee,
            "nonce": self.nonce,
            "hash": self.hash(),
            "signature": self.base64_signature,
        }

    def is_signature_verified(self):
        verification_key = self.sender_pub_key
        try:
            return verification_key.verify(
                signature=self.signature, data=self.hash().encode()
            )
        except ecdsa.BadSignatureError:
            return False

    def create_signature(self, private_key: str):
        """
        Create signature for this transaction
        :param private_key: wallet private key (HEX string)
        :return: None
        """
        private_key_string = bytes.fromhex(private_key)
        private_key = ecdsa.SigningKey.from_string(
            private_key_string, curve=Config.ECDSA_CURVE
        )
        if self.sender_pub_key != private_key.get_verifying_key():
            raise ValidationError("SigningKey is not the sender")
        self.signature = self.sign(private_key)

    def sign(self, private_key: ecdsa.SigningKey):
        return private_key.sign(self.hash().encode())

    def validate(self, blockchain_state):
        """
        Check validation of transaction
        1. check sender key (is valid ECDSA key)
        2. check sender wallet balance
        3. check amount is integer > 0
        4. check fee is integer > 0
        5. check nonce is used only once
        6. check sender signature
        :raises ValidationError
        :return: None
        """

        try:
            _ = self.sender_pub_key
        except ecdsa.MalformedPointError:
            raise ValidationError("invalid sender public key")
        sender_wallet = blockchain_state.wallets.get(self.sender, None)
        if sender_wallet is None or sender_wallet.balance < (self.amount + self.fee):
            if not Config.IS_TEST_NET:
                raise InsufficientBalanceError()
        if sender_wallet is not None and sender_wallet.nonce_counter >= self.nonce:
            raise DuplicateNonceError("Wallet nonce is grater then transaction nonce")
        if type(self.amount) not in (int, float) or self.amount <= 0:
            raise ValidationError("amount must be number grater then 0")
        if type(self.fee) not in (int, float) or self.fee <= 0:
            raise ValidationError("fee must be number grater then 0")
        if not self.is_signature_verified():
            raise ValidationError("transaction signature is not valid")

    def _raw_transaction(self):
        return f"{self.sender}:{self.recipient}:{self.amount}:{self.fee}:{self.nonce}"

    def hash(self):
        transaction_string = self._raw_transaction().encode()
        return hashlib.sha256(transaction_string).hexdigest()

    @property
    def sender_pub_key(self) -> ecdsa.VerifyingKey:
        sender_public_key_string = bytes.fromhex(self.sender)
        sender_verifying_key = ecdsa.VerifyingKey.from_string(
            sender_public_key_string, curve=Config.ECDSA_CURVE
        )
        return sender_verifying_key

    @property
    def base64_signature(self):
        return b64encode(self.signature).decode()

    @classmethod
    def from_dict(cls, sender, recipient, signature, **kwargs):
        signature = b64decode(signature.encode())
        return Transaction(
            sender=sender, recipient=recipient, signature=signature, **kwargs
        )
