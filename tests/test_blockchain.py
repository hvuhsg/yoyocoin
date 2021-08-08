import hashlib
import json
from unittest import TestCase
from time import time

import ecdsa
from src.blockchain import Blockchain, ValidationError, InsufficientBalanceError


class BlockchainTestCase(TestCase):
    @staticmethod
    def create_wallet(secret: str = None):
        if secret is None:
            private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        else:
            private_key = ecdsa.SigningKey.from_secret_exponent(
                secexp=int.from_bytes(secret.encode(), "little"), curve=ecdsa.SECP256k1
            )
        public_key = private_key.get_verifying_key()
        private_address = private_key.to_string().hex()
        public_address = public_key.to_string().hex()
        return {
            "pub_key": public_key,
            "pri_key": private_key,
            "pub_addr": public_address,
            "pri_addr": private_address,
            "nonce_counter": 0,
        }

    def get_blockchain(self) -> Blockchain:
        return Blockchain.get_main_chain()

    def get_rich_wallet_and_poor_wallet(self):
        """
        :return: Rich wallet, poor wallet
        """
        return self.create_wallet(secret="YOYO_DEVELOP_KEY"), self.create_wallet()

    def setUp(self):
        self.blockchain = Blockchain()

        self.wallet_a = self.create_wallet()
        self.wallet_b = self.create_wallet()

    def create_block(self, forger: str, forger_private_addr: str):
        blockchain = self.get_blockchain()
        return blockchain.new_block(forger, forger_private_addr=forger_private_addr)

    def create_transaction(
        self,
        sender: str,
        recipient: str,
        amount: float,
        fee: float,
        sender_private_addr: str,
        nonce: int,
    ):
        return self.get_blockchain().new_transaction(
            sender=sender,
            recipient=recipient,
            amount=amount,
            fee=fee,
            nonce=nonce,
            sender_private_addr=sender_private_addr,
        )


class TestBlocksAndTransactions(BlockchainTestCase):
    def test_block_creation(self):
        blockchain = self.get_blockchain()
        private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        public_key = private_key.get_verifying_key()
        block = self.create_block(forger=public_key.to_string().hex(), forger_private_addr=private_key.to_string().hex())

        # The genesis block is create at initialization, so the length should be 2
        assert block.index == 1
        assert time() - block.timestamp < 2  # Block is timestamp is less then 2 seconds ago
        assert block.previous_hash == blockchain.last_block.hash()
        assert len(block.transactions) == 0
        assert block.forger == public_key.to_string().hex()
        assert block.is_signature_verified()
        blockchain.validate_block(block)

    def test_invalid_signature_block(self):
        blockchain = self.get_blockchain()
        private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        public_key = private_key.get_verifying_key()
        private_key2 = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        with self.assertRaises(ValidationError):
            self.create_block(
                forger=public_key.to_string().hex(), forger_private_addr=private_key2.to_string().hex()
            )

    def test_create_transaction(self):
        blockchain = self.get_blockchain()
        rich_wallet, poor_wallet = self.get_rich_wallet_and_poor_wallet()
        transaction = self.create_transaction(
            sender=rich_wallet["pub_addr"],
            recipient=poor_wallet["pub_addr"],
            fee=1,
            amount=10.5,
            nonce=1,
            sender_private_addr=rich_wallet["pri_addr"],
        )

        assert transaction
        assert transaction.sender == rich_wallet["pub_addr"]
        assert transaction.recipient == poor_wallet["pub_addr"]
        assert transaction.amount == 10.5
        assert transaction.fee == 1
        assert transaction.is_signature_verified()
        blockchain.validate_transaction(transaction)

    def test_invalid_signature_transaction(self):
        rich_wallet, poor_wallet = self.get_rich_wallet_and_poor_wallet()
        with self.assertRaises(ValidationError):
            self.create_transaction(
                sender=rich_wallet["pub_addr"],
                recipient=poor_wallet["pub_addr"],
                fee=1,
                amount=10.5,
                nonce=1,
                sender_private_addr=poor_wallet["pri_addr"],
            )

    def test_insufficient_balance_transaction(self):
        blockchain = self.get_blockchain()
        rich_wallet, poor_wallet = self.get_rich_wallet_and_poor_wallet()
        transaction = self.create_transaction(
            sender=poor_wallet["pub_addr"],
            recipient=rich_wallet["pub_addr"],
            fee=1,
            amount=10.5,
            nonce=1,
            sender_private_addr=poor_wallet["pri_addr"],
        )
        with self.assertRaises(ValidationError):
            blockchain.validate_transaction(transaction)

    def test_zero_amount_transaction(self):
        blockchain = self.get_blockchain()
        rich_wallet, poor_wallet = self.get_rich_wallet_and_poor_wallet()
        transaction = self.create_transaction(
            sender=rich_wallet["pub_addr"],
            recipient=poor_wallet["pub_addr"],
            fee=1,
            amount=0,
            nonce=1,
            sender_private_addr=rich_wallet["pri_addr"],
        )
        with self.assertRaises(ValidationError):
            blockchain.validate_transaction(transaction)

    def test_zero_fee_transaction(self):
        blockchain = self.get_blockchain()
        rich_wallet, poor_wallet = self.get_rich_wallet_and_poor_wallet()
        transaction = self.create_transaction(
            sender=rich_wallet["pub_addr"],
            recipient=poor_wallet["pub_addr"],
            fee=0,
            amount=10,
            nonce=1,
            sender_private_addr=rich_wallet["pri_addr"],
        )
        with self.assertRaises(ValidationError):
            blockchain.validate_transaction(transaction)

    def test_block_validation_when_added_to_chain(self):
        private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        private_key2 = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        public_key = private_key.get_verifying_key()
        with self.assertRaises(ValidationError):
            self.create_block(
                forger=public_key.to_string().hex(),
                forger_private_addr=private_key2.to_string().hex()
            )
