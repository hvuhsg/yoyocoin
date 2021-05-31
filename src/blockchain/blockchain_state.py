from .block import Block


class BlockchainState:
    def __init__(self):
        self.wallets = {}  # type: dict
        self.total_coins = 0  # type: int
        self.score = 0  # type: float
        self.length = 0  # type: int
        self.last_block_hash = None  # type: str
        self.last_block = None  # type: Block

    def add_block(self, block: Block):
        block.validate(blockchain_state=self)
        fees = 0
        for transaction in block.transactions:
            if block.index == 0:
                wallet = self.wallets.get(transaction.recipient)
                if not wallet:
                    self.wallets[transaction.recipient] = {"balance": 0, "last_won": 0, "used_nonce": []}
                self.wallets[transaction.recipient]['balance'] += transaction.amount
                continue
            self.wallets[transaction.sender]['balance'] -= transaction.amount
            self.wallets[transaction.sender]["used_nonce"].append(transaction.nonce)
            recipient_wallet = self.wallets.get(transaction.recipient, None)
            if recipient_wallet is None:
                recipient_wallet = {'balance': 0, 'last_won': 0, 'used_nonce': []}
                self.wallets[transaction.recipient] = recipient_wallet
            self.wallets[transaction.recipient]['balance'] += transaction.amount
            self.wallets[transaction.sender]['balance'] -= transaction.fee
            fees += transaction.fee
        # TODO: update score
        # TODO: update forger "last_won" field
        self.wallets[block.forger]['balance'] += fees
        # self.wallets[block.forger]['last_won'] = block.index  # TODO: add in production
        self.last_block = block
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

    def get_current_lottery_number(self) -> float:
        """
        Calculate the current lottery number base of the last block hash + block signature's
        :return: number (float) in range of 0-100
        """
        pass

    def find_winners(self, lottery_number: float) -> list:
        """
        Find the winners of the lottery (number of wallets)
        :param lottery_number: number (float) in 0-100 range
        :return: list of wallet address
        """
        lottery_wallets = filter(lambda w: wallet[1]['balance'] > 100, self.wallets.items())
        # lottery_wallets = [('A45FR3DssDWCd43e...', {'balance': 127, ...}), ...]

        winners = []
        count = 0
        for wallet in sorted(lottery_wallets, key=lambda w: wallet[0]):
            wallet_percentage = self.wallet_percentage(wallet[0])
            if count + wallet_percentage >= lottery_number:
                winners.append(wallet)
                break
            count += self.wallet_percentage(wallet[0])
        return winners
