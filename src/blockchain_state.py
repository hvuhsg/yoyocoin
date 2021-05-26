from collections import defaultdict


class BlockchainState:
    def __init__(self):
        self.wallets = defaultdict(lambda: dict())
        self.score = 0
        self.blocks = []

    def add_block(self, block):
        block.validate(blockchain_state=self)
        for transaction in block.transactions:
            transaction.validate(blockchain_state=self)
            self.wallets[transaction.sender]['balance'] -= transaction.amount
            self.wallets[transaction.recipient]['balance'] += transaction.amount

        # TODO: update score

    def add_chain(self, chain):
        for block in chain:
            self.add_block(block)

