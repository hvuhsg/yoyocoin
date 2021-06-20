import random
import json
import hashlib
from base64 import b64encode, b64decode
import ecdsa

from .exceptions import ValidationError, InsufficientBalanceError, DuplicateNonce


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
        raw_transaction = self._raw_transaction()
        return {
            **raw_transaction,
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
        :param private_key: base64(wallet private key)
        :return: None
        """
        private_key_string = b64decode(private_key.encode())
        private_key = ecdsa.SigningKey.from_string(private_key_string)
        if self.sender_pub_key != private_key.get_verifying_key():
            raise ValueError("SigningKey is not the sender")
        self.signature = self.sign(private_key)

    def sign(self, private_key: ecdsa.SigningKey):
        return private_key.sign(self.hash().encode())

    def validate(self, blockchain_state, is_test_net=False):
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
        if sender_wallet is None or sender_wallet["balance"] < (self.amount + self.fee):
            if not is_test_net:
                raise InsufficientBalanceError()
        if type(self.amount) != int or self.amount <= 0:
            raise ValidationError("amount must be integer grater then 0")
        if type(self.fee) != int or self.fee <= 0:
            raise ValidationError("fee must be integer grater then 0")
        if not self.is_signature_verified():
            raise ValidationError("transaction signature is not valid")

    def _raw_transaction(self):
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "fee": self.fee,
            "nonce": self.nonce,
        }

    def hash(self):
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        transaction_string = json.dumps(
            self._raw_transaction(), sort_keys=True
        ).encode()
        return hashlib.sha256(transaction_string).hexdigest()

    @property
    def sender_pub_key(self) -> ecdsa.VerifyingKey:
        sender_public_key_string = b64decode(self.sender.encode())
        sender_verifying_key = ecdsa.VerifyingKey.from_string(sender_public_key_string)
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
