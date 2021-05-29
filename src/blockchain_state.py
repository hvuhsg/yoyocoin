from collections import defaultdict


class BlockchainState:
    def __init__(self):
        self.wallets = defaultdict(lambda: dict())
        self.total_coins = 0
        self.score = 0
        self.length = 0
        self.last_block_hash = []

    def add_block(self, block):
        block.validate(blockchain_state=self)
        for transaction in block.transactions:
            if block.index == 0:
                self.wallets[transaction.recipient]['balance'] = transaction.amount
                self.wallets[transaction.recipient]['last_won'] = 0
                self.wallets[transaction.recipient]['used_nonce'] = []
                continue
            self.wallets[transaction.sender]['balance'] -= transaction.amount
            recipient_wallet = self.wallets.get(transaction.recipient, None)
            if recipient_wallet is None:
                recipient_wallet = {'balance': 0, 'last_won': 0, 'used_nonce': []}
                self.wallets[transaction.recipient] = recipient_wallet
            self.wallets[transaction.recipient]['balance'] += transaction.amount
            self.wallets[transaction.sender]['balance'] -= transaction.fee
            self.wallets[block.forger]['balance'] += transaction.fee
        # TODO: update score
        self.last_block_hash = block.hash()
        self.length += 1

    def add_chain(self, chain):
        for block in chain:
            self.add_block(block)

    def wallet_percentage(self, wallet_address: str):
        """
        Wallet percentage in the network
        :param wallet_address: wallet public key as base64
        :return: float in range 0-100
        """
        wallet_balance = self.wallets[wallet_address]
        return wallet_balance / (self.total_coins / 100)

    def lottery_distribution(self):
        lottery_wallets = filter(lambda wallet: wallet[1]['balance'] > 100, self.wallets.items())
        # lottery_wallets = [('A45FR3DssDWCd43e...', {'balance': 127, ...}), ...]
        list(sorted(lottery_wallets, key=lambda wallet: wallet[0]))
        pass

