from typing import Dict

from .consensus import SumTree, wallet_score
from .block import Block
from .exceptions import DuplicateNonceError
from .remote_wallet import RemoteWallet


class BlockchainState:
    def __init__(self):
        self.wallets = {}  # type: Dict[str, RemoteWallet]
        self.sorted_wallets = []  # Sorted by wallet address aka public key
        self.wallets_sum_tree: SumTree = None

        self.score = 0  # type: float
        self.length = 0  # type: int
        self.block_hashs = []  # type: list

        self.last_block_hash = None  # type: str
        self.last_block = None  # type: Block

    def _chain_extended(self):
        # Building the tree
        self.wallets_sum_tree: SumTree = SumTree.from_dict(
            {w.power: index for index, w in enumerate(self.sorted_wallets)}
        )

    def _add_new_wallet(self, wallet: RemoteWallet):
        self.wallets[wallet.address] = wallet
        self.sorted_wallets.append(wallet)
        self.sorted_wallets.sort(key=lambda w: w.address)

    def _get_wallet(self, wallet_address) -> RemoteWallet:
        wallet = self.wallets.get(wallet_address, None)
        if wallet:
            return wallet
        wallet = RemoteWallet.new_empty(wallet_address)
        self._add_new_wallet(wallet)
        return wallet

    def _calculate_wallet_score(self, wallet: RemoteWallet):
        if not self.wallets_sum_tree:
            self._chain_extended()
        lottery_number = 0.3512
        # TODO: change to random value based on last 4 block's hash
        score = wallet_score(
            self.wallets_sum_tree,
            wallet,
            lottery_number=lottery_number,
            wallets_sorted_by_address=self.sorted_wallets,
        )
        # print(f"Wallet {wallet.address} score: {score}")
        return score

    def block_score(self, block: Block) -> int:
        forger_wallet_address = block.forger
        forger_wallet = self._get_wallet(forger_wallet_address)
        return self._calculate_wallet_score(forger_wallet)

    def add_block(self, block: Block):
        block.validate(blockchain_state=self)
        fees = 0
        forger_wallet = self._get_wallet(block.forger)
        forger_score = (
            100 if self.length == 0 else self._calculate_wallet_score(forger_wallet)
        )
        # TODO change from 100 to 0 after lottery system refactor

        for transaction in block.transactions:
            if block.index == 0:  # Genesis block
                recipient_wallet = self._get_wallet(transaction.recipient)
                recipient_wallet.balance += transaction.amount
                continue
            sender_wallet = self._get_wallet(transaction.sender)
            recipient_wallet = self._get_wallet(transaction.recipient)

            if transaction.nonce < sender_wallet.nonce_counter:
                raise DuplicateNonceError()

            sender_wallet.nonce_counter += 1
            sender_wallet.balance -= transaction.amount
            sender_wallet.balance -= transaction.fee

            recipient_wallet.balance += transaction.amount

            sender_wallet.last_transaction = block.index
            recipient_wallet.last_transaction = block.index

            fees += transaction.fee
        forger_wallet.balance += fees
        forger_wallet.last_transaction = block.index

        self.score += forger_score
        self.last_block = block
        self.last_block_hash = block.hash()
        self.block_hashs.append(self.last_block_hash)
        self.length += 1

        self._chain_extended()  # consensus algorithm update

    def add_chain(self, chain):
        for block in chain:
            self.add_block(block)
