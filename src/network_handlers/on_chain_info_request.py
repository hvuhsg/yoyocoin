"""
Handle chain info request
if chain info request is initiated the handler will execute those steps:
1. validate message
2. get chain info and summery
3. publish chain info and get cid
4. send the cid and summery
"""
from typing import Tuple
from ipfs import Node, MessageInterface, Message


class ChainInfoRequestHandler:
    topic = "chain-request"
    topic_response = "chain-response"

    def __init__(self, node: Node):
        self.node = node
        self._cid = None

    def validate(self, message: MessageInterface):
        return True

    def get_chain_info(self) -> Tuple[dict, dict]:
        """
        Return blockchain block hashes
        :return: tuple of chain info (block hashes) and chain summery (chain length and score)
        """
        return {"a": "hello my self"}, {"score": 123}

    def publish_chain_info(self, chain_info: dict) -> str:
        return self.node.create_cid(chain_info)

    def send_cid_and_summery(self, cid: str, summery: dict):
        return self.node.publish_to_topic(topic=self.topic_response, message=Message(cid=cid, meta=summery))

    def __call__(self, message: MessageInterface):
        print(message)
        if not self.validate(message):
            return
        chain_info, chain_summery = self.get_chain_info()
        cid = self.publish_chain_info(chain_info)
        self.send_cid_and_summery(cid, chain_summery)


