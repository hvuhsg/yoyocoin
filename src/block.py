import json
import hashlib
from time import time
from base64 import b64encode

from .transaction import Transaction


class Block:
    def __init__(
            self,
            index,
            previous_hash,
            timestamp=None,
            forger=None,
            transactions=None,
            block_signature=None
    ):
        """
        Create block
        :param index: the block index at the chain (0 for the genesis block and so on)
        :param previous_hash: hash of previous block
        :param timestamp: block creation time
        :param forger: public key of the forger
        :param transactions: list of transactions
        :param block_signature: signature of the block hash by the forger
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
        self.block_signature = block_signature

    def __getitem__(self, item):
        return getattr(self, item)

    @property
    def hash(self):
        """
        Calculate the block hash (block number, previous hash, transactions)
        :return: String hash of block data (hex)
        """

        block_dict = self._raw_data()
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block_dict, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def add_transaction(self, transaction: Transaction):
        """
        Add transaction to block
        :param transaction: Transaction object (see transaction.py)
        :raise Validation error if transaction isn't valid.
        :return: None
        """
        self.transactions.append(transaction)

    def _raw_data(self):
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'previous_hash': self.previous_hash,
            'forger': b64encode(self.forger).decode(),
        }

    def to_dict(self):
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'previous_hash': self.previous_hash,
            'forger': self.forger,
            'hash': self.hash,
        }

    def validate(self):
        pass
