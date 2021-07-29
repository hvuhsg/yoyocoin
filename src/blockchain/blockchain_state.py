from typing import Dict
from .consensus import SumTree, wallet_score

from .block import Block
from .exceptions import DuplicateNonceError


class RemoteWallet:
    def __init__(
        self,
        public_address: str,
        balance: float,
        last_transaction: int,
        nonce_counter: int,
    ):
        self.address = public_address
        self.balance = balance
        self.last_transaction = last_transaction
        self.nonce_counter = nonce_counter

    @property
    def power(self) -> float:
        return self.balance / self.last_transaction

    def __gt__(self, other) -> bool:
        return self.balance > other.address

    def __eq__(self, other):
        return self.address == other.address

    @classmethod
    def new_empty(cls, wallet_address: str):
        return cls(
            public_address=wallet_address,
            balance=0,
            last_transaction=0,
            nonce_counter=0,
        )


class BlockchainState:
    def __init__(self, is_test_net=False):
        self.wallets = {}  # type: Dict[str, RemoteWallet]
        self.sorted_wallets = []  # Sorted by wallet address aka public key
        self.wallets_sum_tree: SumTree = None

        self.total_score = 0

        self.total_coins = 0  # type: int

        self.score = 0  # type: float
        self.length = 0  # type: int
        self.block_hashs = []  # type: list

        self.last_block_hash = None  # type: str
        self.last_block = None  # type: Block

        self.is_test_net = is_test_net

    def _chain_extended(self):
        # Building the tree
        self.wallets_sum_tree: SumTree = SumTree.from_dict(
            {w.power(): index for index, w in enumerate(self.sorted_wallets)}
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
        lottery_number = 0.3321
        # TODO: change to random value based on last 4 block's hash
        return wallet_score(
            self.wallets_sum_tree,
            wallet.address,
            lottery_number=lottery_number,
            wallets_sorted_by_address=self.sorted_wallets,
        )

    def block_score(self, block: Block):
        forger_wallet_address = block.forger
        forger_wallet = self._get_wallet(forger_wallet_address)
        return self._calculate_wallet_score(forger_wallet)

    def add_block(self, block: Block, part_of_chain=False):
        block.validate(blockchain_state=self, is_test_net=self.is_test_net)
        fees = 0
        for transaction in block.transactions:
            if block.index == 0:
                recipient_wallet = self._get_wallet(transaction.recipient)
                recipient_wallet.balance += transaction.amount
                continue
            sender_wallet = self._get_wallet(transaction.sender)
            recipient_wallet = self._get_wallet(transaction.recipient)
            if transaction.nonce != sender_wallet.nonce_counter:
                raise DuplicateNonceError()
            sender_wallet.nonce_counter += 1
            sender_wallet.balance -= transaction.amount
            sender_wallet.balance -= transaction.fee
            recipient_wallet.balance += transaction.amount
            sender_wallet.last_transaction = block.index
            fees += transaction.fee
        forger_wallet = self._get_wallet(block.forger)
        forger_wallet.balance += fees
        self.score += self._calculate_wallet_score(forger_wallet)
        forger_wallet.last_transaction = block.index
        self.last_block = block
        self.last_block_hash = block.hash()
        self.block_hashs.append(self.last_block_hash)
        self.length += 1
        if not part_of_chain:
            self._chain_extended()

    def add_chain(self, chain):
        for block in chain:
            self.add_block(block, part_of_chain=True)
        self._chain_extended()
