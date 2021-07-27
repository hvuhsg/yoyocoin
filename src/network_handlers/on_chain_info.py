"""
Handle chain info request
if chain info response is sent the handler will execute those steps:
1. validate message
2. if chain summery is not relevant ignore message
3. get chain info via cid
4. update chain info
"""
from ipfs import Node, MessageInterface


class ChainInfoHandler:
    topic = "chain-response"

    def __init__(self, node: Node):
        self.node = node

    def validate(self, message: MessageInterface):
        return True

    def message_is_relevant(self, message: MessageInterface) -> bool:
        return message.has_cid()

    def load_chain_info(self, message: MessageInterface) -> str:
        cid = message.get_cid()
        return self.node.load_cid(cid)

    def __call__(self, message: MessageInterface):
        print(message)
        if not self.validate(message):
            return
        if not self.message_is_relevant(message):
            return
        chain_info = self.load_chain_info(message)
        print(chain_info)
        # TODO: update chain with new info


