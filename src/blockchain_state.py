from collections import defaultdict

from src.block import Block


class BlockchainState:
    def __init__(self):
        self.wallets = defaultdict(lambda: dict())
        self.score = 0
        self.blocks = []

    def add_block(self, block: Block):
        if block.index != len(self.blocks):
            raise IndexError("Block index is not valid for this state")
        for transaction in block.transactions:
            if len(self.blocks) == 0 and block.index == 0:  # It is the genesis block
                self.wallets[transaction.recipient]['balance'] = transaction.amount
                continue
            self.wallets[transaction.sender]['balance'] -= transaction.amount
            self.wallets[transaction.recipient]['balance'] += transaction.amount
        # TODO: update score

    def add_chain(self, chain):
        for block in chain:
            self.add_block(block)

