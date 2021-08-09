"""
Handle chain info request
if chain info request is initiated the handler will execute those steps:
1. validate message
2. get chain info and summery
3. publish chain info and get cid
4. send the cid and summery
"""
from typing import Tuple

from blockchain import Blockchain
from network.ipfs import Node, Message

from .handler import Handler


class ChainInfoRequestHandler(Handler):
    topic = "chain-request"
    topic_response = "chain-response"

    def __init__(self, node: Node):
        self.node = node
        self._cid = None

    def validate(self, message: Message):
        blockchain: Blockchain = Blockchain.get_main_chain()
        score_exist = message.meta.get("score", None) is not None
        score_is_lower = (
            score_exist and message.meta.get("score") < blockchain.score
        )
        # TODO: check length
        return score_is_lower

    def get_chain_info(self) -> Tuple[dict, dict]:
        """
        Return blockchain block hashes
        :return: tuple of chain info (block hashes) and chain summery (chain length and score)
        """
        blockchain: Blockchain = Blockchain.get_main_chain()
        blocks = blockchain.chain
        score = blockchain.score
        length = blockchain.length
        return {"blocks": blocks}, {"score": score, "length": length}

    def publish_chain_info(self, chain_info: dict) -> str:
        blocks_cids = []
        blocks_hashes = []
        for block in chain_info["blocks"]:
            block_dict = block.to_dict()
            blocks_cids.append(self.node.create_cid(block_dict))
            blocks_hashes.append(block.hash())
        return self.node.create_cid(
            {"blocks_cid": blocks_cids, "blocks_hash": blocks_hashes}
        )

    def send_cid_and_summery(self, cid: str, summery: dict):
        return self.node.publish_to_topic(
            topic=self.topic_response, message=Message(cid=cid, meta=summery)
        )

    def __call__(self, message: Message):
        super().log(message)
        if not self.validate(message):
            return
        chain_info, chain_summery = self.get_chain_info()
        cid = self.publish_chain_info(chain_info)
        self.send_cid_and_summery(cid, chain_summery)
