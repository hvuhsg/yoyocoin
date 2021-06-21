from typing import List
from urllib.parse import urlparse

from .exceptions import ValidationError
from .constents import GENESIS_BLOCK
from .transaction import Transaction
from .block import Block
from .blockchain_state import BlockchainState


class Blockchain:
    def __init__(self, pruned=True, is_test_net=False):
        self.current_transactions: List[Transaction] = []
        self.chain: List[Block] = []
        self.chain_length = 0
        self.nodes = set()
        self.state = BlockchainState(is_test_net=is_test_net)
        self.pruned = pruned
        self.is_test_net = is_test_net
        if self.is_test_net:
            self.default_genesis()

    def default_genesis(self):
        genesis_block = Block.from_dict(**GENESIS_BLOCK)
        self.add_block(genesis_block)

    def create_genesis(
        self,
        developer_pub_address,
        developer_pri_key,
        developer_pri_address,
        initial_coins: int,
    ):
        create_coins_transaction = Transaction(
            sender="0", recipient=developer_pub_address, amount=initial_coins, nonce=0
        )
        signature = create_coins_transaction.sign(developer_pri_key)
        create_coins_transaction.signature = signature
        transactions = [create_coins_transaction]
        genesis_block = Block(
            index=0,
            previous_hash="0",
            transactions=transactions,
            forger=developer_pub_address,
        )
        genesis_block.create_signature(developer_pri_address)
        self.add_block(genesis_block)

    def new_block(self, forger, forger_private_addr, previous_hash=None, index=None):
        """
        Create a new Block in the Blockchain

        TODO: replace with PoS
        block: the new Block object
        :return: New Block
        """
        if previous_hash is None:
            previous_hash = self.last_block.hash()
        if index is None:
            index = self.state.length
        new_block = Block(index=index, previous_hash=previous_hash, forger=forger)

        new_block.transactions = sorted(
            self.current_transactions, key=lambda t: t.nonce
        )
        if new_block.index > 0:
            new_block.create_signature(forger_private_addr)

        # Reset the current list of transactions
        self.current_transactions = []

        return new_block

    def add_block(self, block):
        if self.pruned:
            self.chain = [block]
        else:
            self.chain.append(block)
        self.chain_length += 1
        for tx in block.transactions:
            try:
                self.current_transactions.remove(tx)
            except ValueError:
                pass
        self.state.add_block(block)

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
        new_transaction.validate(
            blockchain_state=self.state, is_test_net=self.is_test_net
        )
        self.current_transactions.append(new_transaction)

        return new_transaction

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_stake(self, last_block, forger_key):
        """
        Simple Proof of Stake Algorithm:

         - Find the lottery number
         - If your wallet address is close create block and sign it

        :param last_block: <dict> last Block
        :param forger_key: <str> forger public key
        :return: <int>
        """

        # TODO: create lottery number generator
        pass
