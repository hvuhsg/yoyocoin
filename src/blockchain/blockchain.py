from typing import List
from urllib.parse import urlparse

import requests

from .exceptions import ValidationError
from .constents import GENESIS_BLOCK
from .transaction import Transaction
from .block import Block
from .blockchain_state import BlockchainState


class Blockchain:
    def __init__(self):
        self.current_transactions: List[Transaction] = []
        self.chain: List[Block] = []
        self.nodes = set()
        self.state = BlockchainState()

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

    def register_node(self, address):
        """
        Add a new node to the list of nodes

        :param address: Address of node. Eg. 'http://192.168.0.5:5000'
        """

        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError("Invalid URL")

    @staticmethod
    def valid_chain(chain):
        """
        Determine if a given blockchain is valid

        :param chain: A blockchain
        :return: True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f"{last_block}")
            print(f"{block}")
            print("\n-----------\n")
            # Check that the hash of the block is correct
            last_block_hash = last_block.hash
            if block["previous_hash"] != last_block_hash:
                return False
            try:
                block.validate()
            except ValidationError:
                return False
            last_block = block
            current_index += 1
        return True

    @staticmethod
    def chain_score(chain):
        return 1  # TODO: create chain score calculation algorithm

    def resolve_conflicts(self):
        """
        This is our consensus algorithm, it resolves conflicts
        by replacing our chain with the chain with the most score on the network.

        :return: True if our chain was replaced, False if not
        """

        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains with more score then ours
        max_score = self.chain_score(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f"http://{node}/chain")

            if response.status_code == 200:
                response_score = response.json()["score"]
                if response_score < max_score:
                    continue
                chain = response.json()["chain"]
                if not self.valid_chain(chain):
                    continue  # decrease node integrity score
                actual_score = self.chain_score(chain)
                if actual_score != response_score:
                    pass  # decrease node integrity score

                # Check if the length is longer and the chain is valid
                if actual_score > max_score:
                    max_score = actual_score
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain with more score than ours
        if new_chain:
            self.chain = new_chain
            return True
        return False

    def new_block(self, forger, forger_private_addr, previous_hash=None, index=None):
        """
        Create a new Block in the Blockchain

        TODO: replace with PoS
        block: the new Block object
        :return: New Block
        """
        if previous_hash is None:
            previous_hash = self.last_block.hash()
            index = len(self.chain)
        new_block = Block(index=index, previous_hash=previous_hash, forger=forger)

        new_block.transactions = sorted(self.current_transactions, key=lambda t: t.nonce)
        if new_block.index > 0:
            new_block.create_signature(forger_private_addr)

        # Reset the current list of transactions
        self.current_transactions = []

        self.add_block(new_block)
        return new_block

    def add_block(self, block):
        self.chain.append(block)
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
        :return: The index of the Block that will hold this transaction
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
        new_transaction.validate(blockchain_state=self.state)
        self.current_transactions.append(new_transaction)

        return self.last_block.index + 1

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
