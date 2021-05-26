import hashlib
import json
from base64 import b64encode
from unittest import TestCase

import ecdsa
from src.blockchain import Blockchain


class BlockchainTestCase(TestCase):

    def setUp(self):
        self.blockchain = Blockchain()

        self.private_key = ecdsa.SigningKey.generate()
        self.public_key = self.private_key.get_verifying_key()
        self.private_address = b64encode(self.private_key.to_string()).decode()
        self.public_address = b64encode(self.public_key.to_string()).decode()

        self.private_key_2 = ecdsa.SigningKey.generate()
        self.public_key_2 = self.private_key_2.get_verifying_key()
        self.private_address_2 = b64encode(self.private_key_2.to_string()).decode()
        self.public_address_2 = b64encode(self.public_key_2.to_string()).decode()

    def create_block(self, forger=None, forger_private_key=None):
        if forger is None:
            forger = self.public_address
        if forger_private_key is None:
            forger_private_key = self.private_address
        self.blockchain.new_block(forger, forger_private_key)

    def create_transaction(
            self,
            sender=None,
            recipient=None,
            amount=1,
            sender_private_key=None,
    ):
        if sender is None:
            sender = self.public_address
        if recipient is None:
            recipient = self.public_address_2
        if sender_private_key is None:
            sender_private_key = self.private_address
        self.blockchain.new_transaction(
            sender=sender, recipient=recipient, amount=amount, sender_private_key=sender_private_key
        )


class TestRegisterNodes(BlockchainTestCase):

    def test_valid_nodes(self):
        blockchain = Blockchain()

        blockchain.register_node('http://192.168.0.1:5000')

        self.assertIn('192.168.0.1:5000', blockchain.nodes)

    def test_malformed_nodes(self):
        blockchain = Blockchain()

        blockchain.register_node('http//192.168.0.1:5000')

        self.assertNotIn('192.168.0.1:5000', blockchain.nodes)

    def test_idempotency(self):
        blockchain = Blockchain()

        blockchain.register_node('http://192.168.0.1:5000')
        blockchain.register_node('http://192.168.0.1:5000')

        assert len(blockchain.nodes) == 1


class TestBlocksAndTransactions(BlockchainTestCase):

    def test_block_creation(self):
        self.create_block()

        latest_block = self.blockchain.last_block

        # The genesis block is create at initialization, so the length should be 2
        assert len(self.blockchain.chain) == 2
        assert latest_block['index'] == 1
        assert latest_block['timestamp'] is not None
        assert latest_block['previous_hash'] == self.blockchain.chain[-2].hash()
        assert latest_block['forger'] == self.public_address

    def test_create_transaction(self):
        self.create_transaction()

        transaction = self.blockchain.current_transactions[-1]

        assert transaction
        assert transaction.sender == self.public_address
        assert transaction.recipient == self.public_address_2
        assert transaction.amount == 1
        assert transaction.is_signature_verified()

    def test_block_resets_transactions(self):
        self.create_transaction()

        initial_length = len(self.blockchain.current_transactions)

        self.create_block()

        current_length = len(self.blockchain.current_transactions)

        assert initial_length == 1
        assert current_length == 0

    def test_return_last_block(self):
        self.create_block()

        created_block = self.blockchain.last_block

        assert len(self.blockchain.chain) == 2
        assert created_block.index == 1
        assert created_block is self.blockchain.chain[-1]


class TestHashingAndProofs(BlockchainTestCase):

    def test_block_hash_is_correct(self):
        self.create_block()

        new_block = self.blockchain.last_block
        new_block_json = json.dumps(new_block._raw_data(), sort_keys=True).encode()
        new_hash = hashlib.sha256(new_block_json).hexdigest()

        assert len(new_hash) == 64
        assert new_hash == new_block.hash()

    def test_transaction_hash_is_correct(self):
        self.create_transaction()

        new_transaction = self.blockchain.current_transactions[-1]
        new_transaction_json = json.dumps(new_transaction._raw_transaction(), sort_keys=True).encode()
        new_hash = hashlib.sha256(new_transaction_json).hexdigest()

        assert len(new_hash) == 64
        assert new_hash == new_transaction.hash()


class TextKeysSignatureAndVerification(BlockchainTestCase):

    def test_transaction_signature_creation(self):
        self.create_transaction()
        new_transaction = self.blockchain.current_transactions[-1]

        assert new_transaction.is_signature_verified()
        assert self.public_key.verify(new_transaction.signature, new_transaction.hash().encode())

        # The signature is verified but the signing key not sign the same signature every time
        assert self.private_key.sign(b"test") != self.private_key.sign(b"test")
        assert new_transaction.sign(private_key=self.private_key) != new_transaction.signature

        correct_signature = new_transaction.signature
        new_transaction.signature = new_transaction.sign(private_key=self.private_key_2)
        assert (not new_transaction.is_signature_verified())
        new_transaction.signature = correct_signature

    def test_block_signature_creation(self):
        self.create_block()
        new_block = self.blockchain.last_block

        assert new_block.is_signature_verified()
        assert self.public_key.verify(new_block.signature, new_block.hash().encode())

        # The signature is verified but the signing key not sign the same signature every time
        assert self.private_key.sign(b"test") != self.private_key.sign(b"test")
        assert new_block.sign(self.private_key) != new_block.sign(self.private_key)

        correct_signature = new_block.signature
        new_block.signature = new_block.sign(forger_private_key=self.private_key_2)
        assert (not new_block.is_signature_verified())
        new_block.signature = correct_signature
