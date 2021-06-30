from threading import Thread

from blockchain import Blockchain, Block
from .network_manager import NetworkManager
from .client import Client


class ChainSyncer:
    def __init__(self, blockchain: Blockchain, network_manager: NetworkManager, is_test_net: bool = False):
        self.blockchain = blockchain
        self.network_manager = network_manager
        self.best_chain = None
        self.best_chain_node = None
        self.best_chain_score = 0
        self.is_test_net = is_test_net

    def _find_best_chain(self):
        for node in self.network_manager.outbound_connections.copy():
            url = self.network_manager.url_from_address(node)
            chain_info = Client.request_chain_info(url)
            print(url, chain_info["score"])
            if not chain_info:
                continue
            if chain_info["length"] > self.blockchain.chain_length and chain_info["score"] > self.best_chain_score:
                self.best_chain_score = chain_info["score"]
                self.best_chain = chain_info
                self.best_chain_node = url

    def _get_chain_data(self):
        start = 0
        for my_block_hash, there_block_hash in zip(self.blockchain.state.block_hashs, self.best_chain["hashs"]):
            if my_block_hash == there_block_hash:
                start += 1
        blocks = Client.get_chain_blocks(url=self.best_chain_node, start=start)["blocks"]
        new_chain = Blockchain(is_test_net=self.is_test_net)
        print("start", start)
        print([(a, b) for a, b in zip(self.blockchain.state.block_hashs, self.best_chain["hashs"])])
        print(self.blockchain.chain)
        for i in range(1, start):
            new_chain.add_block(self.blockchain.chain[i])
        for block in blocks:
            b = Block.from_dict(**block)
            new_chain.add_block(b)
        print(new_chain.state.score)
        print(new_chain.chain_length)
        if new_chain.state.score > self.blockchain.state.score:
            self.blockchain.update_chain(new_chain)
            print("Save sync chain")

    def sync_chain(self):
        print("Start sync")
        self._find_best_chain()
        print("Find best chain", self.best_chain_score)
        if self.best_chain_score <= self.blockchain.state.score:
            return
        print("Verifying blockchain")
        self._get_chain_data()

    def sync(self):
        self.best_chain_node = None
        self.best_chain_score = 0
        self.best_chain = None

        t = Thread(target=self.sync_chain)
        t.daemon = True
        t.start()
