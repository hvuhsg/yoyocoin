from enum import Enum

from wallet import Wallet
from blockchain import Block, Blockchain, ValidationError
from scheduler import Scheduler
from node.blueprints.protocol import Protocol
from node.blueprints.message import Message

from .sync_protocol import SyncProtocol


class LotteryManager:
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


class Routes(Enum):
    NewBlock = 0


class LotteryProtocol(Protocol):
    name: str = "LotteryProtocol"

    def __init__(self):
        super().__init__()
        self.lottery_manager = LotteryManager()
        Scheduler.get_instance().add_job(
            func=self.broadcast_best_block_so_far,
            name="broadcast_best_lottery_block",
            interval=20,
            sync=False,
            run_thread=True,
        )

    def broadcast_best_block_so_far(self):
        if self.lottery_manager.winning_block is None:
            return
        message = self.send_best_block(self.lottery_manager.winning_block)
        self.broadcast(message)

    def process(self, message: Message) -> dict:
        if Routes(message.route) == Routes.NewBlock:
            return self.process_best_block(message)

    def process_best_block(self, message: Message):
        blockchain: Blockchain = Blockchain.get_main_chain()

        if "block" not in message.params:
            return {"Error": "block is required"}
        block = message.params["block"]
        block = Block.from_dict(**block)
        result = self.lottery_manager.check_lottery_block(block)
        if not result and blockchain.state.length < block.index:
            return SyncProtocol.request_chain_info()

    def send_best_block(self, block: Block) -> Message:
        return Message.from_dict({
            "protocol": self.__class__.name,
            "route": Routes.NewBlock.value,
            "params": {"block": block.to_dict()}
        })
