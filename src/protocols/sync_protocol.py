from enum import Enum

from blockchain import Blockchain, Block
from node.blueprints.protocol import Protocol
from node.blueprints.message import Message


class Routes(Enum):
    ChainInfoRequest = 0
    ChainInfoResponse = 1
    ChainBlocksRequest = 2
    ChainBlocksResponse = 3


class SyncProtocol(Protocol):
    name: str = "SyncProtocol"

    def process(self, message: Message) -> dict:
        if Routes(message.route) == Routes.ChainInfoRequest:
            return self.chain_info_response()
        elif Routes(message.route) == Routes.ChainInfoResponse:
            return self.check_chain_info(message)
        elif Routes(message.route) == Routes.ChainBlocksRequest:
            return self.blocks_request(message)
        elif Routes(message.route) == Routes.ChainBlocksResponse:
            self.sync_chain(message)

    @classmethod
    def request_chain_info(cls):
        return Message(protocol=cls.name, route=Routes.ChainInfoRequest.value)

    def sync_chain(self, message: Message):
        main_chain: Blockchain = Blockchain.get_main_chain()

        start = message.params.get("start", None)
        blocks = message.params.get("blocks", None)
        if start is None or blocks is None:
            return
        if start + len(blocks) <= main_chain.state.length:
            return

        main_chain: Blockchain = Blockchain.get_main_chain()
        sync_blockchain = Blockchain(is_test_net=main_chain.is_test_net)
        for i in range(1, start):
            sync_blockchain.add_block(main_chain.chain[i])
        for block in message.params.get("blocks"):
            block = Block.from_dict(**block)
            sync_blockchain.add_block(block)
        if sync_blockchain.state.score > main_chain.state.score \
            and sync_blockchain.state.length > main_chain.state.length:
            Blockchain.set_main_chain(sync_blockchain)
            print("Blockchain synced!")

    def blocks_request(self, message: Message):
        blockchain = Blockchain.get_main_chain()
        start = message.params.get("start", None)
        if start is None:
            return
        blocks = blockchain.chain[start:]
        return Message(
            protocol=self.__class__.name,
            route=Routes.ChainBlocksResponse.value,
            params={"blocks": [block.to_dict() for block in blocks], "start": start}
        )

    def check_chain_info(self, message: Message):
        blockchain: Blockchain = Blockchain.get_main_chain()
        if message.params["score"] <= blockchain.state.score:
            return
        elif message.params["length"] < blockchain.state.length:
            return
        elif len(message.params["hashs"]) != message.params["length"]:
            return
        my_hashs = blockchain.state.block_hashs
        start = 0
        for my_hash, there_hash in zip(my_hashs, message.params["hashs"]):
            if my_hash != there_hash:
                break
            start += 1
        return Message.from_dict(
            {"protocol": self.__class__.name, "route": Routes.ChainBlocksRequest.value, "params": {"start": start}}
        )

    def chain_info_response(self):
        blockchain: Blockchain = Blockchain.get_main_chain()
        return Message.from_dict({
            "protocol": self.__class__.name,
            "route": Routes.ChainInfoResponse.value,
            "params": {
                "hashs": blockchain.state.block_hashs,
                "score": blockchain.state.score,
                "length": blockchain.state.length
            }
        })
