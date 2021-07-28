"""
Handle new block
if new block is sent, the handler will execute those steps:
1. validate message
2. if block hash and index are relevant (block is needed and I don't have it yet)
3. get new block via cid
4. parse new block and verify it
4. add block to chain
"""
from blockchain import Block, Blockchain
from ipfs import Node, MessageInterface, Message

from .handler import Handler


class NewBlockHandler(Handler):
    topic = "new-block"

    def __init__(self, node: Node):
        self.node = node

    def validate(self, message: Message):
        return message.has_cid() and "p_hash" in message.meta and "index" in message.meta

    def message_is_relevant(self, message: Message) -> bool:
        blockchain: Blockchain = Blockchain.get_main_chain()
        p_hash = message.meta.get("p_hash")
        block_index = message.meta.get("index")
        p_hash_is_valid = blockchain.last_block.hash() == p_hash
        index_is_valid = blockchain.last_block.index + 1 == block_index
        return p_hash_is_valid and index_is_valid

    def load_block(self, message: MessageInterface) -> dict:
        cid = message.get_cid()
        return self.node.load_cid(cid)

    def parse_block(self, block_dict: dict) -> Block:
        return Block.from_dict(**block_dict)

    def add_block_to_blockchain(self, block: Block):
        blockchain: Blockchain = Blockchain.get_main_chain()
        blockchain.add_block(block)
        print("Block added to blockchain", "\n    - index:", block.index)

    def __call__(self, message: MessageInterface):
        super().log(message)
        if not self.validate(message):
            return
        if not self.message_is_relevant(message):
            return
        block_dict = self.load_block(message)
        block = self.parse_block(block_dict)
        self.add_block_to_blockchain(block)


