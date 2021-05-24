import hashlib
from urllib.parse import urlparse

import requests

from src.transaction import Transaction
from src.block import Block


class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()

        # Create the genesis block
        self.new_block(previous_hash='1', proof=100, forger=b'')

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

    def valid_chain(self, chain):
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

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof'], last_block_hash, block['miner']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        This is our consensus algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.

        :return: True if our chain was replaced, False if not
        """

        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def new_block(self, proof, previous_hash, forger):
        """
        Create a new Block in the Blockchain

        :param proof: The proof given by the Proof of Work algorithm TODO: replace with PoS
        :param previous_hash: Hash of previous Block
        :param forger: public key of the forger (to get reward)
        :return: New Block
        """
        if previous_hash is None:
            previous_hash = self.last_block.hash
        block = Block(
            index=len(self.chain)+1,
            transactions=self.current_transactions,
            previous_hash=previous_hash,
            forger=forger,
        )

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount, nonce, signature):
        """
        Creates a new transaction to go into the next mined Block

        :param sender: Public key of the Sender (ECDSA)
        :param recipient: Public key of the Recipient (ECDSA)
        :param amount: Coin amount to transfer
        :param signature: Signature of the transaction (ECDSA)
        :param nonce: Number only sent once for double spending protection
        :raise ValueError: when the signature doesn't match the transaction.
        :return: The index of the Block that will hold this transaction
        """
        transaction = Transaction(sender=sender, recipient=recipient, amount=amount, nonce=nonce, signature=signature)
        if transaction.is_signature_verified() is False:
            raise ValueError("Invalid Signature")
        self.current_transactions.append(transaction.to_dict())

        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_block, miner_key):
        """
        Simple Proof of Work Algorithm:

         - Find a number p' such that hash(pp') contains leading 4 zeroes
         - Where p is the previous proof, and p' is the new proof

        :param last_block: <dict> last Block
        :param miner_key: <str> miner public key
        :return: <int>
        """

        last_proof = last_block['proof']
        last_hash = last_block.hash

        proof = 0
        while self.valid_proof(last_proof, proof, last_hash, miner_key) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof, last_hash, miner_key):
        """
        Validates the Proof

        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :param last_hash: <str> The hash of the Previous Block
        :param miner_key: <str> The miner public key
        :return: <bool> True if correct, False if not.

        """

        guess = f'{last_proof}{proof}{last_hash}{miner_key}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
