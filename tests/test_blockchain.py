import hashlib
import json
from base64 import b64encode
from random import randint
from unittest import TestCase

import ecdsa
from src.blockchain import Blockchain, ValidationError


class BlockchainTestCase(TestCase):
    @staticmethod
    def create_wallet():
        private_key = ecdsa.SigningKey.generate()
        public_key = private_key.get_verifying_key()
        private_address = b64encode(private_key.to_string()).decode()
        public_address = b64encode(public_key.to_string()).decode()
        return {
            "pub_key": public_key,
            "pri_key": private_key,
            "pub_addr": public_address,
            "pri_addr": private_address,
            "nonce_counter": 0,
        }

    def setUp(self):
        self.blockchain = Blockchain(pruned=False)
        self.blockchain.default_genesis()

        self.wallet_a = self.create_wallet()
        self.wallet_b = self.create_wallet()

    def setup_blockchain_history(self):
        self.developer_wallet = self.create_wallet()
        self.max_coins = 10000
        self.initial_blocks_number = 5

        self.blockchain = Blockchain()
        self.blockchain.create_genesis(
            developer_pub_address=self.developer_wallet["pub_addr"],
            developer_pri_address=self.developer_wallet["pri_addr"],
            developer_pri_key=self.developer_wallet["pri_key"],
            initial_coins=self.max_coins,
        )

        wallets = [self.create_wallet() for i in range(20)]
        for wallet in wallets:
            recipient_wallet = wallet
            self.create_transaction(
                sender=self.developer_wallet,
                recipient=recipient_wallet,
                amount=300,
            )
        self.create_block(
            forger=self.developer_wallet["pub_addr"],
            forger_private_addr=self.developer_wallet["pri_addr"],
        )
        for _ in range(self.initial_blocks_number - 1):
            for _ in range(5):
                sender_wallet = wallets[randint(0, len(wallets) - 1)]
                recipient_wallet = wallets[randint(0, len(wallets) - 1)]
                self.create_transaction(
                    sender=sender_wallet,
                    recipient=recipient_wallet,
                    amount=randint(1, 2),
                )
            self.create_block(
                forger=self.developer_wallet["pub_addr"],
                forger_private_addr=self.developer_wallet["pri_addr"],
            )

        a_index = randint(0, len(wallets) - 1)
        b_index = a_index + 1 if a_index != len(wallets) - 1 else a_index - 1
        self.wallet_a = wallets[a_index]
        self.wallet_b = wallets[b_index]

    def create_block(self, forger=None, forger_private_addr=None):
        if forger is None:
            forger = self.developer_wallet["pub_addr"]
        if forger_private_addr is None:
            forger_private_addr = self.developer_wallet["pri_addr"]
        block = self.blockchain.new_block(forger, forger_private_addr)
        self.blockchain.add_block(block)

    def create_transaction(
        self, sender=None, recipient=None, amount=1, fee=1, sender_private_addr=None
    ):
        if sender is None:
            sender = self.wallet_a
        if recipient is None:
            recipient = self.wallet_b
        if sender_private_addr is None:
            sender_private_addr = sender["pri_addr"]
        self.blockchain.new_transaction(
            sender=sender["pub_addr"],
            recipient=recipient["pub_addr"],
            amount=amount,
            fee=fee,
            nonce=sender["nonce_counter"],
            sender_private_addr=sender_private_addr,
        )
        sender["nonce_counter"] += 1


class TestBlocksAndTransactions(BlockchainTestCase):
    def setUp(self):
        self.setup_blockchain_history()

    def test_block_creation(self):
        self.create_block()

        latest_block = self.blockchain.last_block

        # The genesis block is create at initialization, so the length should be 2
        assert latest_block["index"] == self.initial_blocks_number + 1
        assert latest_block["timestamp"] is not None
        if not self.blockchain.pruned and self.blockchain.chain_length > 1:
            assert latest_block["previous_hash"] == self.blockchain.chain[-2].hash()

    def test_create_transaction(self):
        self.create_transaction()

        transaction = self.blockchain.current_transactions[-1]

        assert transaction
        assert transaction.sender == self.wallet_a["pub_addr"]
        assert transaction.recipient == self.wallet_b["pub_addr"]
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

        assert created_block.index == self.initial_blocks_number + 1
        assert created_block is self.blockchain.chain[-1]


class TestHashingAndProofs(BlockchainTestCase):
    def setUp(self):
        self.setup_blockchain_history()

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
        new_transaction_json = json.dumps(
            new_transaction._raw_transaction(), sort_keys=True
        ).encode()
        new_hash = hashlib.sha256(new_transaction_json).hexdigest()

        assert len(new_hash) == 64
        assert new_hash == new_transaction.hash()


class TestKeysSignatureAndVerification(BlockchainTestCase):
    def setUp(self):
        self.setup_blockchain_history()

    def test_transaction_signature_creation(self):
        self.create_transaction()
        new_transaction = self.blockchain.current_transactions[-1]

        assert new_transaction.is_signature_verified()
        assert self.wallet_a["pub_key"].verify(
            new_transaction.signature, new_transaction.hash().encode()
        )

        # The signature is verified but the signing key not sign the same signature every time
        assert self.wallet_a["pri_key"].sign(b"test") != self.wallet_a["pri_key"].sign(
            b"test"
        )
        assert (
            new_transaction.sign(private_key=self.wallet_a["pri_key"])
            != new_transaction.signature
        )

        correct_signature = new_transaction.signature
        new_transaction.signature = new_transaction.sign(
            private_key=self.wallet_b["pri_key"]
        )
        assert not new_transaction.is_signature_verified()
        new_transaction.signature = correct_signature

    def test_block_signature_creation(self):
        self.create_block()
        new_block = self.blockchain.last_block

        assert new_block.is_signature_verified()
        assert self.developer_wallet["pub_key"].verify(
            new_block.signature, new_block.hash().encode()
        )

        # The signature is verified but the signing key not sign the same signature every time
        assert new_block.sign(self.developer_wallet["pri_key"]) != new_block.sign(
            self.developer_wallet["pri_key"]
        )

        correct_signature = new_block.signature
        new_block.signature = new_block.sign(
            forger_private_key=self.wallet_b["pri_key"]
        )
        assert not new_block.is_signature_verified()
        new_block.signature = correct_signature


class TestInvalidTransactions(BlockchainTestCase):
    def setUp(self):
        self.setup_blockchain_history()

    def test_no_balance_sender(self):
        new_empty_wallet = self.create_wallet()
        self.assertRaises(
            ValidationError,
            self.create_transaction,
            sender=new_empty_wallet,
            recipient=self.wallet_a,
            amount=1,
        )

    def test_send_more_then_balance(self):
        new_empty_wallet = self.create_wallet()
        self.assertRaises(
            ValidationError,
            self.create_transaction,
            sender=new_empty_wallet,
            recipient=self.wallet_a,
            amount=self.max_coins + 1,
        )

    def test_invalid_amount(self):
        self.assertRaises(
            ValidationError,
            self.create_transaction,
            sender=self.wallet_b,
            recipient=self.wallet_a,
            amount=-1,
        )
        self.assertRaises(
            ValidationError,
            self.create_transaction,
            sender=self.wallet_b,
            recipient=self.wallet_a,
            amount=0,
        )

    def test_invalid_fee(self):
        self.assertRaises(
            ValidationError,
            self.create_transaction,
            sender=self.wallet_b,
            recipient=self.wallet_a,
            amount=1,
            fee=-1,
        )

        self.assertRaises(
            ValidationError,
            self.create_transaction,
            sender=self.wallet_b,
            recipient=self.wallet_a,
            amount=1,
            fee=0,
        )
