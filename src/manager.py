from .storage import Storage
from .node import BlockchainNode
from .blockchain import Blockchain


class Manager:
    def __init__(self):
        self.storage = Storage()
        self.node = BlockchainNode()
        self.blockchain = Blockchain()

    def new_block_callback(self, block):
        pass

    def new_transaction_callback(self, transaction):
        pass
