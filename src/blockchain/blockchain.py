from typing import Dict, List

from config import Config

from .constants import GENESIS_BLOCK
from .transaction import Transaction
from .block import Block
from .blockchain_state import BlockchainState


class Blockchain:
    main_chain = None

    @classmethod
    def set_main_chain(cls, blockchain):
        cls.main_chain = blockchain

    @classmethod
    def get_main_chain(cls):
        return cls.main_chain

    def __init__(self, branch: bool = False):
        if self.__class__.main_chain is not None and not branch:
            raise RuntimeError("Singleton can initialized only once. use get_main_chain() or mark as branch")
        self.current_transactions: Dict[
            str, Transaction
        ] = {}  # {transaction hash: transaction object}
        self.chain: List[Block] = []
        self.chain_length = 0
        self.__state: BlockchainState = BlockchainState()
        self.pruned = not Config.IS_FULL_NODE
        self.default_genesis()

        self.set_main_chain(self)

    @property
    def last_block(self):
        return self.chain[-1]

    @property
    def score(self):
        return self.__state.score

    @property
    def length(self):
        return self.__state.length

    @property
    def block_hashs(self):
        return self.__state.block_hashs

    @property
    def wallets(self):
        return self.__state.wallets

    @property
    def sorted_wallets(self):
        return self.__state.sorted_wallets

    def default_genesis(self):
        genesis_block = Block.from_dict(**GENESIS_BLOCK)
        self.add_block(genesis_block)

    def new_block(self, forger, previous_hash=None, index=None, signature=None):
        """
        Create a new Block in the Blockchain

        block: the new Block object
        :return: New Block
        """
        if previous_hash is None:
            previous_hash = self.last_block.hash()
        if index is None:
            index = self.__state.length
        new_block = Block(
            index=index, previous_hash=previous_hash, forger=forger, signature=signature
        )

        new_block.transactions = sorted(
            self.current_transactions.values(),
            key=lambda t: t.nonce + (1 / int.from_bytes(t.hash().encode(), "little")),
        )

        return new_block

    def add_block(self, block: Block):
        if block.signature is None:
            raise ValueError("Block is unsigned!")
        self.__state.add_block(block)
        for tx in block.transactions:
            self.current_transactions.pop(tx.hash(), None)
        if self.pruned:
            self.chain = [block]
        else:
            self.chain.append(block)
        self.chain_length += 1

    def new_transaction(
        self,
        sender,
        recipient,
        amount,
        nonce: int,
        fee=1,
        signature: str = None,
    ):
        """
        Creates a new transaction to go into the next mined Block

        :param nonce: wallet transaction counter (for preventing duplicate transactions)
        :param signature: transaction signature (signed by the sender)
        :param fee: integer >= 1
        :param amount: integer > 0
        :param recipient: recipient public key
        :param sender: sender public key
        :raise ValueError: when the signature doesn't match the transaction.
        :return: The transaction object
        """
        new_transaction = Transaction(
            sender=sender,
            recipient=recipient,
            amount=amount,
            fee=fee,
            nonce=nonce,
            signature=signature,
        )
        return new_transaction

    def add_transaction(self, transaction: Transaction):
        transaction.validate(blockchain_state=self.__state)
        self.current_transactions[transaction.hash()] = transaction

    def add_chain(self, blocks: list):
        self.__state.add_chain(blocks)
        self.chain.extend(blocks)
        self.chain_length += len(blocks)

    def validate_block(self, block: Block):
        return block.validate(self.__state)

    def validate_transaction(self, transaction: Transaction):
        return transaction.validate(self.__state)

    def get_block_score(self, block: Block):
        return self.__state.block_score(block=block)

    # TODO: create lottery number generator


def setup_blockchain():
    #  TODO: load from disk
    blockchain = Blockchain()
    Blockchain.set_main_chain(blockchain)

