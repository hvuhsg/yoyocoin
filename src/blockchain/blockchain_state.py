from math import e
from .block import Block
from .constents import MAX_BLOCKS_FOR_SCORE


class BlockchainState:
    def __init__(self):
        self.wallets = {}  # type: dict
        self.total_coins = 0  # type: int
        self.score = 0  # type: float
        self.length = 0  # type: int
        self.last_block_hash = None  # type: str
        self.last_block = None  # type: Block

    def _new_wallet_data(self):
        return {"balance": 0, "used_nonce": [], "last_transaction": 0}

    def _get_wallet(self, wallet_address):
        wallet = self.wallets.get(wallet_address, None)
        if wallet:
            return wallet
        self.wallets[wallet_address] = self._new_wallet_data()
        return self.wallets[wallet_address]

    def _calculate_forger_score(self, forger_wallet):
        current_block_index = self.length
        blocks_number = min((current_block_index - forger_wallet["last_transaction"]), MAX_BLOCKS_FOR_SCORE)
        multiplier = (blocks_number**e)/(111**e)+0.0000000001
        return forger_wallet["balance"] * multiplier

    def add_block(self, block: Block):
        block.validate(blockchain_state=self)
        fees = 0
        for transaction in block.transactions:
            if block.index == 0:
                recipient_wallet = self._get_wallet(transaction.recipient)
                recipient_wallet['balance'] += transaction.amount
                continue
            sender_wallet = self._get_wallet(transaction.sender)
            recipient_wallet = self._get_wallet(transaction.recipient)

            sender_wallet['balance'] -= transaction.amount
            sender_wallet['balance'] -= transaction.fee
            sender_wallet["used_nonce"].append(transaction.nonce)
            recipient_wallet['balance'] += transaction.amount
            sender_wallet["last_transaction"] = block.index
            sender_wallet["last_transaction"] = block.index
            fees += transaction.fee
        forger_wallet = self._get_wallet(block.forger)
        forger_wallet['balance'] += fees
        self.score += self._calculate_forger_score(forger_wallet)
        forger_wallet["last_transaction"] = block.index
        self.last_block = block
        self.last_block_hash = block.hash()
        self.length += 1

    def add_chain(self, chain):
        for block in chain:
            self.add_block(block)

