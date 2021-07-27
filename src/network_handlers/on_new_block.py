"""
Handle new block
if new block is sent, the handler will execute those steps:
1. validate message
2. if block hash and index are relevant (block is needed and I don't have it yet)
3. get new block via cid
4. parse new block and verify it
4. add block to chain
"""
from blockchain import Block
from ipfs import Node, MessageInterface, Message


class NewBlockHandler:
    topic = "new-block"

    def __init__(self, node: Node):
        self.node = node

    def validate(self, message: Message):
        return message.has_cid() and "hash" in message.meta and "index" in message.meta

    def message_is_relevant(self, message: Message) -> bool:
        block_hash = message.meta.get("hash")
        block_index = message.meta.get("index")
        # TODO: check if block is all ready stored
        # TODO: check the block index is relevant (the next block)
        return True

    def load_block(self, message: MessageInterface) -> dict:
        cid = message.get_cid()
        return self.node.load_cid(cid)

    def parse_block(self, block_dict: dict) -> Block:
        return Block.from_dict(**block_dict)

    def __call__(self, message: MessageInterface):
        if not self.validate(message):
            return
        if not self.message_is_relevant(message):
            return
        block_dict = self.load_block(message)
        block = self.parse_block(block_dict)
        print(block.to_dict())
        # TODO: add block to blockchain


