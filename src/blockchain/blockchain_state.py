import math
from hashlib import sha256
from random import choices, seed, random

from .block import Block
from .constents import (
    MAX_BLOCKS_FOR_SCORE,
    MAX_BALANCE_FOR_SCORE,
    BLOCKS_CURVE_NUMBER,
    MIN_SCORE,
    LOTTERY_PRIZES,
    LOTTERY_WEIGHTS,
)
from .exceptions import DuplicateNonce


class BlockchainState:
    def __init__(self, is_test_net=False):
        self.wallets = {}  # type: dict

        self.total_coins = 0  # type: int

        self.score = 0  # type: float
        self.length = 0  # type: int
        self.block_hashs = []  # type: list

        self.last_block_hash = None  # type: str
        self.last_block = None  # type: Block

        self.is_test_net = is_test_net

    def _new_wallet_data(self, wallet_address):
        return {
            "balance": 0,
            "nonce_counter": 0,
            "last_transaction": 0,
            "address": wallet_address,
        }

    def _get_wallet(self, wallet_address):
        wallet = self.wallets.get(wallet_address, None)
        if wallet:
            return wallet
        self.wallets[wallet_address] = self._new_wallet_data(wallet_address)
        return self.wallets[wallet_address]

    def _calculate_lottery_block_bonus(self, wallet_address: str):
        seed(f"{wallet_address}{self.last_block_hash}")
        lottery_multiplier = choices(LOTTERY_PRIZES, LOTTERY_WEIGHTS)[0]
        return lottery_multiplier

    def _tie_break(self, wallet_address: str) -> float:
        seed(f"{wallet_address}{self.last_block_hash}")
        return random()

    def _calculate_forger_score(self, forger_wallet):
        current_block_index = self.length
        blocks_number = min(
            (current_block_index - forger_wallet["last_transaction"]),
            MAX_BLOCKS_FOR_SCORE,
        )
        lottery_blocks = self._calculate_lottery_block_bonus(forger_wallet["address"])
        blocks_number += lottery_blocks
        multiplier = (blocks_number ** math.e + MIN_SCORE) / (
            BLOCKS_CURVE_NUMBER ** math.e
        )
        wallet_balance = min(forger_wallet["balance"], MAX_BALANCE_FOR_SCORE)
        score = wallet_balance * multiplier
        tie_brake_number = self._tie_break(forger_wallet["address"])
        return score + MIN_SCORE + tie_brake_number

    def block_score(self, block: Block):
        forger_wallet_address = block.forger
        forger_wallet = self._get_wallet(forger_wallet_address)
        return self._calculate_forger_score(forger_wallet)

    def add_block(self, block: Block):
        block.validate(blockchain_state=self, is_test_net=self.is_test_net)
        fees = 0
        for transaction in block.transactions:
            if block.index == 0:
                recipient_wallet = self._get_wallet(transaction.recipient)
                recipient_wallet["balance"] += transaction.amount
                continue
            sender_wallet = self._get_wallet(transaction.sender)
            recipient_wallet = self._get_wallet(transaction.recipient)
            if transaction.nonce != sender_wallet["nonce_counter"]:
                raise DuplicateNonce()
            sender_wallet["nonce_counter"] += 1
            sender_wallet["balance"] -= transaction.amount
            sender_wallet["balance"] -= transaction.fee
            recipient_wallet["balance"] += transaction.amount
            sender_wallet["last_transaction"] = block.index
            sender_wallet["last_transaction"] = block.index
            fees += transaction.fee
        forger_wallet = self._get_wallet(block.forger)
        forger_wallet["balance"] += fees
        self.score += self._calculate_forger_score(forger_wallet)
        forger_wallet["last_transaction"] = block.index
        self.last_block = block
        self.last_block_hash = block.hash()
        self.block_hashs.append(self.last_block_hash)
        self.length += 1

    def add_chain(self, chain):
        for block in chain:
            self.add_block(block)
