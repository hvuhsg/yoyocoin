from typing import Dict, List

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

    def __init__(self, pruned=False, is_test_net=False):
        self.current_transactions: Dict[
            str, Transaction
        ] = {}  # {transaction hash: transaction object}
        self.chain: List[Block] = []
        self.chain_length = 0
        self.__state: BlockchainState = BlockchainState(is_test_net=is_test_net)
        self.pruned = pruned
        self.is_test_net = is_test_net
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

    def new_block(self, forger, forger_private_addr, previous_hash=None, index=None):
        """
        Create a new Block in the Blockchain

        block: the new Block object
        :return: New Block
        """
        if previous_hash is None:
            previous_hash = self.last_block.hash()
        if index is None:
            index = self.__state.length
        new_block = Block(index=index, previous_hash=previous_hash, forger=forger)

        new_block.transactions = sorted(
            self.current_transactions.values(),
            key=lambda t: t.nonce + (1 / int.from_bytes(t.hash().encode(), 'little'))
        )
        if new_block.index > 0:
            new_block.create_signature(forger_private_addr)

        # Reset the current list of transactions
        self.current_transactions = {}
        # TODO: remove transaction on block link to chain

        return new_block

    def add_block(self, block: Block):
        for tx in block.transactions:
            self.current_transactions.pop(tx.hash(), None)
        self.__state.add_block(block)
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
        sender_private_addr=None,
        signature=None,
    ):
        """
        Creates a new transaction to go into the next mined Block

        :param nonce: wallet transaction counter (for preventing duplicate transactions)
        :param signature: transaction signature (signed by the sender)
        :param fee: integer >= 1
        :param sender_private_addr: sender private key : string
        :param amount: integer > 0
        :param recipient: recipient public key
        :param sender: sender public key
        :raise ValueError: when the signature doesn't match the transaction.
        :return: The transaction object
        """
        if not (sender_private_addr or signature):
            raise ValueError("required signature or private address")
        new_transaction = Transaction(
            sender=sender,
            recipient=recipient,
            amount=amount,
            fee=fee,
            nonce=nonce,
            signature=signature,
        )
        if sender_private_addr is not None:
            new_transaction.create_signature(sender_private_addr)

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

