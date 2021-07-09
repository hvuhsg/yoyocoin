from blockchain import Blockchain, Block, ValidationError
from wallet import Wallet
from scheduler import Scheduler
from globals.singleton import Singleton

from ..connections_manager import ConnectionManager, get_connection_manager
from ..blueprints.message import Message


class LotteryManager(Singleton):
    def __init__(self):
        self.wallet = Wallet.get_main_wallet()
        self.nodes_lottery_status = {}
        self.winning_block = None
        self.best_score = 0
        self.register_interval_functions()

        super().__init__()

    @property
    def blockchain(self):
        return Blockchain.get_main_chain()

    def register_interval_functions(self):
        Scheduler.get_instance().add_job(
            func=self.declare_winner,
            name="insert_winning_block_to_chain",
            interval=60,
            sync=True,
            run_thread=True,
            offset=5,
        )
        Scheduler.get_instance().add_job(
            func=self.create_block,
            name="create_lottery_block",
            interval=60,
            sync=True,
            run_thread=True,
        )
        Scheduler.get_instance().add_job(
            func=self.broadcast_best_block_so_far,
            name="broadcast_best_lottery_block",
            interval=20,
            sync=False,
            run_thread=True,
        )

    def reset_lottery(self):
        self.nodes_lottery_status = {}
        self.winning_block = None
        self.best_score = 0

    def check_lottery_block(self, block: Block) -> bool:
        """
        Check if this block have the best score so far on this lottery
        if it is set as winning block else discard
        :param block: new forged block (block index must be sequential with the blockchain)
        :return: True if is the best score so far else False
        """
        if block.index != self.blockchain.state.length or block.previous_hash != self.blockchain.state.last_block_hash:
            return False
        score = self.blockchain.state.block_score(block)
        if score > self.best_score:
            self.winning_block = block
            self.best_score = score
            return True
        return False

    def declare_winner(self):
        if self.winning_block is not None:
            try:
                self.blockchain.add_block(self.winning_block)
            except ValidationError:
                pass
            else:
                print("lottery winner", self.winning_block.index, self.winning_block.hash())
            finally:
                self.reset_lottery()

    def create_block(self):
        block = self.blockchain.new_block(
            forger=self.wallet.public_address, forger_private_addr=self.wallet.private_address
        )
        self.check_lottery_block(block)

    @staticmethod
    def new_block(self, block: Block) -> Message:
        return Message.from_dict({
            "protocol": self.__class__.name,
            "route": 0,
            "params": {"block": block.to_dict()}
        })

    def broadcast_best_block_so_far(self):
        if self.winning_block is None:
            return
        connections_manager: ConnectionManager = get_connection_manager()
        message = self.new_block(self.winning_block)
        connections_manager.broadcast(message)
