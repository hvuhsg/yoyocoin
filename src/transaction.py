import random
import json
import hashlib
from base64 import b64encode, b64decode
import ecdsa

from .exceptions import ValidationError


class Transaction:
    def __init__(self, sender, recipient, amount, nonce=None, signature=None):
        if nonce is None:
            nonce = random.randrange(-1*(2**60), 2**60)
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.nonce = nonce
        self.signature = signature

    def to_dict(self):
        raw_transaction = self._raw_transaction()
        return {
            **raw_transaction,
            "hash": self.hash,
            "signature": b64encode(self.signature)
        }

    def is_signature_verified(self):
        verification_key = self.sender_pub_key
        try:
            verification_key.verify(signature=self.signature, data=self.hash.encode())
        except ecdsa.BadSignatureError:
            return False
        return True

    def create_signature(self, private_key: ecdsa.SigningKey):
        sender_verifying_key = ecdsa.VerifyingKey.from_string(self.sender)
        if sender_verifying_key != private_key.get_verifying_key():
            raise ValueError('SigningKey is not the sender')
        self.signature = self.sign(private_key)

    def sign(self, private_key: ecdsa.SigningKey):
        return private_key.sign(self.hash.encode())

    def validate(self):
        """
        Check validation of transaction
        1. check signature
        2. check sender balance
        :raise ValidationError
        :return: None
        """
        # TODO: validate sender balance
        if not self.is_signature_verified():
            raise ValidationError("transaction signature is not valid")

    def _raw_transaction(self):
        return {
            "sender": b64encode(self.sender).decode(),
            "recipient": b64encode(self.recipient).decode(),
            "amount": self.amount,
            "nonce": self.nonce,
        }

    @property
    def sender_pub_key(self) -> ecdsa.VerifyingKey:
        public_key = ecdsa.VerifyingKey.from_string(self.sender)
        return public_key

    @property
    def hash(self):
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        transaction_string = json.dumps(self._raw_transaction(), sort_keys=True).encode()
        return hashlib.sha256(transaction_string).hexdigest()

    @classmethod
    def from_dict(cls, sender, recipient, signature, **kwargs):
        sender = b64decode(sender)
        recipient = b64decode(recipient)
        signature = b64decode(signature)
        return Transaction(sender=sender, recipient=recipient, signature=signature, **kwargs)
