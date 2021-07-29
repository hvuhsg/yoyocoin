from blockchain import Block, Transaction
from ipfs import Message, Node


class NetworkApi:
    @staticmethod
    def create_cid(node: Node, data: dict):
        return node.create_cid(data)

    @staticmethod
    def create_message(cid: str = None, meta: dict = None) -> Message:
        if meta is None:
            meta = {}
        return Message(cid=cid, meta=meta)

    @staticmethod
    def send_message(node: Node, topic: str, message: Message):
        node.publish_to_topic(topic, message)

    @staticmethod
    def send_block(node: Node, block: Block):
        block_cid = NetworkApi.create_cid(node, data=block.to_dict())
        message = NetworkApi.create_message(
            cid=block_cid, meta={"index": block.index, "hash": block.hash()}
        )
        NetworkApi.send_message(node, topic="new-block", message=message)

    @staticmethod
    def send_transaction(node: Node, transaction: Transaction):
        transaction_cid = NetworkApi.create_cid(node, data=transaction.to_dict())
        message = NetworkApi.create_message(cid=transaction_cid)
        NetworkApi.send_message(node, topic="new-transaction", message=message)
