from typing import List
from urllib.parse import urlparse

import requests

from .transaction import Transaction
from .block import Block
from .exceptions import ValidationError


class Blockchain:
    def __init__(self):
        self.current_transactions: List[Transaction] = []
        self.chain: List[Block] = []
        self.nodes = set()

        # Create the genesis block
        self.new_block(forger=b'', forger_private_key=b'', previous_hash='0', index=0)

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
            raise ValueError('Invalid URL')

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
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            last_block_hash = last_block.hash
            if block['previous_hash'] != last_block_hash:
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
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                chain = response.json()['chain']
                if not self.valid_chain(chain):
                    continue
                score = self.chain_score(chain)

                # Check if the length is longer and the chain is valid
                if score > max_score:
                    max_score = score
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True
        return False

    def new_block(self, forger, forger_private_key, previous_hash=None, index=None):
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

        new_block.transactions = self.current_transactions
        if new_block.index > 0:
            new_block.create_signature(forger_private_key)

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(new_block)
        return new_block

    def new_transaction(self, sender, recipient, amount, sender_private_key, fee=1):
        """
        Creates a new transaction to go into the next mined Block

        :param fee: integer >= 1
        :param sender_private_key: sender private key : ecdsa.SigningKey
        :param amount: integer > 0
        :param recipient: recipient public key
        :param sender: sender public key
        :raise ValueError: when the signature doesn't match the transaction.
        :return: The index of the Block that will hold this transaction
        """
        new_transaction = Transaction(sender=sender, recipient=recipient, amount=amount, fee=fee)
        new_transaction.create_signature(sender_private_key)
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
