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
from network.ipfs import Node, Message
from event_stream import EventStream, Event

from .handler import Handler


class NewBlockHandler(Handler):
    topic = "new-block"

    def __init__(self):
        self.node = Node.get_instance()

    def validate(self, message: Message):
        return (
            message.has_cid() and "p_hash" in message.meta and "index" in message.meta
        )

    def load_block(self, message: Message) -> dict:
        cid = message.get_cid()
        return self.node.load_cid(cid)

    def parse_block(self, block_dict: dict) -> Block:
        return Block.from_dict(**block_dict)

    def publish_event(self, block: Block):
        event_stream: EventStream = EventStream.get_instance()
        event_stream.publish(topic='new-block-from-network', event=Event(name='new-block', block=block))

    def __call__(self, message: Message):
        super().log(message)
        if not self.validate(message):
            return
        block_dict = self.load_block(message)
        block = self.parse_block(block_dict)
        self.publish_event(block)
