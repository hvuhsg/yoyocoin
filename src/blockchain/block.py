from typing import List
import json
import hashlib
from time import time
from base64 import b64decode, b64encode

import ecdsa

from .constents import BLOCK_COUNT_FREEZE_WALLET_LOTTERY_AFTER_WIN
from .transaction import Transaction
from .exceptions import ValidationError, NonLotteryMember, WalletLotteryFreeze


class Block:
    def __init__(
        self,
        index,
        previous_hash,
        timestamp=None,
        forger=None,
        transactions: List[Transaction] = None,
        signature=None,
        **kwargs
    ):
        """
        Create block
        :param index: the block index at the chain (0 for the genesis block and so on)
        :param previous_hash: hash of previous block
        :param timestamp: block creation time
        :param forger: public_address of forger wallet
        :param transactions: list of transactions
        :param signature: signature of the block hash by the forger
        """
        if timestamp is None:
            timestamp = time()
        if transactions is None:
            transactions = []
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.forger = forger
        self.transactions = transactions
        self.signature = signature

    def __getitem__(self, item):
        return getattr(self, item)

    def _raw_data(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [
                transaction.to_dict() for transaction in self.transactions
            ],
            "previous_hash": self.previous_hash,
            "forger": self.forger,
        }

    @property
    def forger_public_key(self) -> ecdsa.VerifyingKey:
        forger_public_key_string = b64decode(self.forger.encode())
        return ecdsa.VerifyingKey.from_string(forger_public_key_string)

    def hash(self):
        """
        Calculate the block hash (block number, previous hash, transactions)
        :return: String hash of block data (hex)
        """

        block_dict = self._raw_data()
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block_dict, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def create_signature(self, forger_private_address: str):
        """
        Create block signature for this block
        :param forger_private_address: base64(wallet private address)
        :return: None
        """

        forger_private_key_string = b64decode(forger_private_address.encode())
        forger_private_key = ecdsa.SigningKey.from_string(forger_private_key_string)
        if forger_private_key.get_verifying_key() != self.forger_public_key:
            raise ValueError("The forger is not the one signing")
        self.signature = self.sign(forger_private_key)

    def sign(self, forger_private_key: ecdsa.SigningKey):
        return forger_private_key.sign(self.hash().encode())

    def add_transaction(self, transaction: Transaction):
        """
        Add transaction to block
        :param transaction: Transaction object (see transaction.py)
        :raise Validation error if transaction isn't valid.
        :return: None
        """
        self.transactions.append(transaction)

    def is_signature_verified(self) -> bool:
        """
        Check if block signature is valid
        :return: bool
        """
        try:
            return self.forger_public_key.verify(self.signature, self.hash().encode())
        except ecdsa.BadSignatureError:
            return False

    def to_dict(self):
        return {
            **self._raw_data(),
            "hash": self.hash(),
            "signature": b64encode(self.signature).decode(),
        }

    def validate(self, blockchain_state, is_test_net=False):
        """
        Validate block
        1. check block index (is the next block in the blockchain state)
        2. check previous hash (is the hash of the previous block)
        3. check forger wallet (balance > 100)
        4. check block signature
        5. validate transactions

        :param blockchain_state: Blockchain state object
        :raises ValidationError
        :return: None
        """
        if self.index == 0 and blockchain_state.length == 0:
            return  # TODO: check in production if hash if equal to hard coded hash
        if self.index != blockchain_state.length:
            raise ValidationError(f"block index not sequential index: {self.index} chain: {blockchain_state.length}")
        if self.previous_hash != blockchain_state.last_block_hash:
            raise ValidationError("previous hash not match previous block hash")
        forger_wallet = blockchain_state.wallets.get(self.forger, None)
        if forger_wallet is None or forger_wallet["balance"] < 100:
            if not is_test_net:
                raise NonLotteryMember()
        if not self.is_signature_verified():
            raise ValidationError("invalid signature")
        for transaction in self.transactions:
            transaction.validate(
                blockchain_state=blockchain_state, is_test_net=is_test_net
            )  # raises ValidationError
        # TODO: Add timestamp validation

    @classmethod
    def from_dict(
        cls,
        index: int,
        previous_hash,
        forger,
        transactions: dict,
        signature: str,
        **kwargs
    ):
        transactions = list(map(lambda t: Transaction.from_dict(**t), transactions))
        signature = b64decode(signature.encode())
        return cls(
            index=index,
            previous_hash=previous_hash,
            forger=forger,
            transactions=transactions,
            signature=signature,
            **kwargs
        )
