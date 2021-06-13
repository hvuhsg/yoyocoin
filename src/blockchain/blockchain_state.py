import math
from hashlib import sha256
from random import choices, seed

from .block import Block
from .constents import MAX_BLOCKS_FOR_SCORE, MAX_BALANCE_FOR_SCORE, LOTTERY_PRIZES, LOTTERY_WEIGHTS


class BlockchainState:
    def __init__(self):
        self.wallets = {}  # type: dict
        self.total_coins = 0  # type: int
        self.score = 0  # type: float
        self.length = 0  # type: int
        self.last_block_hash = None  # type: str
        self.last_block = None  # type: Block

    def _new_wallet_data(self, wallet_address):
        return {"balance": 0, "nonce_counter": 0, "last_transaction": 0, "address": wallet_address}

    def _get_wallet(self, wallet_address):
        wallet = self.wallets.get(wallet_address, None)
        if wallet:
            return wallet
        self.wallets[wallet_address] = self._new_wallet_data(wallet_address)
        return self.wallets[wallet_address]

    def _calculate_lottery_block_bonus(self, wallet_address: str):
        current_block_index = self.length
        lottery_hash = sha256(f"{current_block_index}{self.last_block_hash}{wallet_address}".encode())
        lottery_number = int.from_bytes(lottery_hash.digest(), "big")
        seed(lottery_number)
        lottery_multiplier = choices(LOTTERY_PRIZES, LOTTERY_WEIGHTS)[0]
        return lottery_multiplier

    def _calculate_forger_score(self, forger_wallet):
        current_block_index = self.length
        blocks_number = min(
            (current_block_index - forger_wallet["last_transaction"]),
            MAX_BLOCKS_FOR_SCORE,
        )
        lottery_blocks = self._calculate_lottery_block_bonus(forger_wallet["address"])
        blocks_number += lottery_blocks
        multiplier = (blocks_number ** math.e + 0.1) / (111 ** math.e)
        wallet_balance = min(forger_wallet["balance"], MAX_BALANCE_FOR_SCORE)
        score = wallet_balance * multiplier
        return score

    def add_block(self, block: Block):
        block.validate(blockchain_state=self)
        fees = 0
        for transaction in block.transactions:
            if block.index == 0:
                recipient_wallet = self._get_wallet(transaction.recipient)
                recipient_wallet["balance"] += transaction.amount
                continue
            sender_wallet = self._get_wallet(transaction.sender)
            recipient_wallet = self._get_wallet(transaction.recipient)
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
        self.length += 1

    def add_chain(self, chain):
        for block in chain:
            self.add_block(block)
