from blockchain import Blockchain, Block
from wallet import Wallet
from scheduler import Scheduler

from .network_manager import NetworkManager


class LotteryManager:
    def __init__(self, blockchain: Blockchain, wallet: Wallet):
        self.blockchain = blockchain
        self.wallet = wallet
        self.winning_block = None
        self.best_score = 0

        self.register_interval_functions()

    def register_interval_functions(self):
        Scheduler.get_instance().add_job(
            func=self.declare_winner,
            name="insert_winning_block_to_chain",
            interval=38,
            sync=True,
            run_thread=False,
        )
        Scheduler.get_instance().add_job(
            func=self.create_block,
            name="create_lottery_block",
            interval=20,
            sync=True,
            run_thread=False,
        )
        Scheduler.get_instance().add_job(
            func=self.broadcast_best_block_so_far,
            name="broadcast_best_lottery_block",
            interval=10,
            sync=True,
            run_thread=True,
        )

    def reset_lottery(self):
        self.winning_block = None
        self.best_score = 0

    def check_lottery_block(self, block: Block) -> bool:
        """
        Check if this block have the best score so far on this lottery
        if it is set as winning block else discard
        :param block: new forged block (block index must be sequential with the blockchain)
        :return: True if is the best score so far else False
        """
        if block.index != self.blockchain.state.length:
            return False
        score = self.blockchain.state.block_score(block)
        if score > self.best_score:
            self.winning_block = block
            self.best_score = score
            return True
        return False

    def declare_winner(self):
        if self.winning_block is not None:
            print("lottery winner", self.winning_block.to_dict())
            self.blockchain.add_block(self.winning_block)
            self.reset_lottery()

    def create_block(self):
        block = self.blockchain.new_block(
            forger=self.wallet.public_address, forger_private_addr=self.wallet.private_address
        )
        self.check_lottery_block(block)

    def broadcast_best_block_so_far(self):
        nm: NetworkManager = NetworkManager.get_instance()
        if self.winning_block is not None:
            nm.broadcast_best_lottery_block(self.winning_block)
