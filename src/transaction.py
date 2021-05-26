import random
import json
import hashlib
from base64 import b64encode, b64decode
import ecdsa

from .exceptions import ValidationError, InsufficientBalanceError, DuplicateNonce
from .blockchain_state import BlockchainState


class Transaction:
    def __init__(self, sender, recipient, amount, fee=None, nonce=None, signature=None):
        if nonce is None:
            nonce = random.randrange(-1*(2**60), 2**60)
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
            "signature": self.base64_signature
        }

    def is_signature_verified(self):
        verification_key = self.sender_pub_key
        try:
            return verification_key.verify(signature=self.signature, data=self.hash().encode())
        except ecdsa.BadSignatureError:
            return False

    def create_signature(self, private_key: ecdsa.SigningKey):
        sender_verifying_key = ecdsa.VerifyingKey.from_string(self.sender)
        if sender_verifying_key != private_key.get_verifying_key():
            raise ValueError('SigningKey is not the sender')
        self.signature = self.sign(private_key)

    def sign(self, private_key: ecdsa.SigningKey):
        return private_key.sign(self.hash().encode())

    def validate(self, blockchain_state: BlockchainState):
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
        # TODO: validate sender balance
        try:
            sender_public_key = self.sender_pub_key
        except ecdsa.MalformedPointError:
            raise ValidationError("invalid sender public key")
        base64_sender = self._raw_transaction()['sender']
        sender_wallet = blockchain_state.wallets.get(base64_sender, None)
        if sender_wallet is None or sender_wallet['balance'] < (self.amount + self.fee):
            raise InsufficientBalanceError()
        if type(self.amount) != int or self.amount <= 0:
            raise ValidationError("amount must be integer grater then 0")
        if type(self.fee) != int or self.fee <= 0:
            raise ValidationError("fee must be integer grater then 0")
        if self.nonce in sender_wallet['used_nonce']:
            raise DuplicateNonce()
        if not self.is_signature_verified():
            raise ValidationError("transaction signature is not valid")

    def _raw_transaction(self):
        return {
            "sender": self.sender_wallet_address,
            "recipient": self.recipient_wallet_address,
            "amount": self.amount,
            "fee": self.fee,
            "nonce": self.nonce,
        }

    def hash(self):
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        transaction_string = json.dumps(self._raw_transaction(), sort_keys=True).encode()
        return hashlib.sha256(transaction_string).hexdigest()

    @property
    def sender_pub_key(self) -> ecdsa.VerifyingKey:
        public_key = ecdsa.VerifyingKey.from_string(self.sender)
        return public_key

    @property
    def sender_wallet_address(self):
        return b64encode(self.sender).decode()

    @property
    def recipient_wallet_address(self):
        return b64encode(self.recipient).decode()

    @property
    def base64_signature(self):
        return b64encode(self.signature).decode()

    @classmethod
    def from_dict(cls, sender, recipient, signature, **kwargs):
        sender = b64decode(sender)
        recipient = b64decode(recipient)
        signature = b64decode(signature)
        return Transaction(sender=sender, recipient=recipient, signature=signature, **kwargs)
