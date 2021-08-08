"""
Handle chain info request
if chain info response is sent the handler will execute those steps:
1. validate message
2. if chain summery is not relevant ignore message
3. get chain info via cid
4. update chain info
"""
from typing import List

from loguru import logger

from blockchain import Blockchain, Block
from network.ipfs import Node, Message

from .handler import Handler


class ChainInfoHandler(Handler):
    topic = "chain-response"

    def __init__(self, node: Node):
        self.node = node

    def validate(self, message: Message):
        cid_exist = message.has_cid()
        score_exist = message.meta.get("score", None) is not None
        length_exist = message.meta.get("length", None) is not None
        length_is_valid = True
        # TODO: validate chain length with network start time
        return cid_exist and score_exist and length_exist and length_is_valid

    def message_is_relevant(self, message: Message) -> bool:
        blockchain: Blockchain = Blockchain.get_main_chain()
        score_is_bigger = message.meta.get("score") > blockchain.state.score
        length_is_bigger = message.meta.get("length") >= blockchain.state.length
        return score_is_bigger and length_is_bigger

    def load_chain_blocks(self, message: Message) -> list:
        cid = message.get_cid()
        blocks = []
        blocks_info = self.node.load_cid(cid)
        for b_cid, b_hash in zip(blocks_info["blocks_cid"], blocks_info["blocks_hash"]):
            block_dict = self.node.load_cid(b_cid)
            block = Block.from_dict(**block_dict)
            if block.hash() != b_hash or (
                blocks and block.previous_hash != blocks[-1].hash()
            ):
                break
            blocks.append(block)
        else:
            return blocks

    def build_blockchain(self, blocks: List[Block]):
        current_blockchain: Blockchain = Blockchain.get_main_chain()
        new_blockchain = Blockchain(is_test_net=current_blockchain.is_test_net)
        if blocks and blocks[0].index == 0:
            blocks.pop(0)
        new_blockchain.add_chain(blocks)
        score_is_bigger = new_blockchain.state.score > current_blockchain.state.score
        length_is_not_lower = (
            new_blockchain.state.length >= current_blockchain.state.length
        )
        if score_is_bigger and length_is_not_lower:
            logger.success(
                "New blockchain synced!"
                + f"\n-\tScore: {new_blockchain.state.score}"
                + f"\n-\tLength: {new_blockchain.state.length}"
            )
            Blockchain.set_main_chain(new_blockchain)

    def __call__(self, message: Message):
        super().log(message)
        if not self.validate(message):
            return
        if not self.message_is_relevant(message):
            return
        chain_blocks = self.load_chain_blocks(message)
        self.build_blockchain(chain_blocks)
