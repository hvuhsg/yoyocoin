from client import Client
from blockchain import Blockchain, Block, ValidationError
from wallet import Wallet
from scheduler import Scheduler
from server.connections_manager.network_manager import NetworkManager


class LotteryManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise RuntimeError(f"{cls.__name__} is not initiated")
        return cls._instance

    def __init__(self):
        self.wallet = Wallet.get_main_wallet()
        self.nodes_lottery_status = {}
        self.winning_block = None
        self.best_score = 0
        self.register_interval_functions()

        self.__class__._instance = self

    @property
    def blockchain(self):
        return Blockchain.get_main_chain()

    def register_interval_functions(self):
        Scheduler.get_instance().add_job(
            func=self.declare_winner,
            name="insert_winning_block_to_chain",
            interval=33,
            sync=True,
            run_thread=True,
        )
        Scheduler.get_instance().add_job(
            func=self.create_block,
            name="create_lottery_block",
            interval=30,
            sync=True,
            run_thread=True,
        )
        Scheduler.get_instance().add_job(
            func=self.broadcast_best_block_so_far,
            name="broadcast_best_lottery_block",
            interval=10,
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
        print("Block index:", block.index, "chain len", self.blockchain.state.length)
        if block.index != self.blockchain.state.length or block.previous_hash != self.blockchain.state.last_block_hash:
            return False
        score = self.blockchain.state.block_score(block)
        if score > self.best_score:
            self.winning_block = block
            self.best_score = score
            print("Is currently winning")
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

    def broadcast_best_block_so_far(self):
        nm: NetworkManager = NetworkManager.get_instance()
        if self.winning_block is None:
            return
        for node in nm.outbound_connections.copy():
            node_lottery_status = self.nodes_lottery_status.get(node, None)
            if node_lottery_status is None or node_lottery_status != self.winning_block.hash():
                url = nm.url_from_address(node)
                Client.send_best_lottery_block(url, self.winning_block.to_dict())
                self.nodes_lottery_status[node] = self.winning_block.hash()
