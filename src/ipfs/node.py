import json
from typing import Callable

from .api import IpfsAPI, Message
from .network_listener import NetworkListener


class CallbackIsNotCallable(TypeError):
    def __init__(self, non_callable):
        self.non_callable = non_callable

    def __str__(self):
        return f"The object {self.non_callable} is not callable!"


class Node:
    def __init__(
        self,
        is_full_node: bool = True,
    ):
        self.ipfs_api = IpfsAPI()

        self.is_full_node = is_full_node

    def publish_to_topic(self, topic: str, message: Message = None):
        if message is None:
            message = Message()
        message.meta.update({"node_id": self.ipfs_api.node_id})
        self.ipfs_api.publish_json_to_topic(topic, message.to_dict())

    def load_cid(self, cid: str):
        return self.ipfs_api.get_data(cid)

    def create_cid(self, data: dict):
        return self.ipfs_api.add_data(json.dumps(data))

    def publish_block(self, block: dict):
        block_json = json.dumps(block)
        cid = self.ipfs_api.add_data(block_json)
        return cid

    def publish_transaction(self, transaction: dict):
        transaction_json = json.dumps(transaction)
        cid = self.ipfs_api.add_data(transaction_json)
        return cid

    def add_listener(self, handler):
        if not callable(handler):
            raise CallbackIsNotCallable(handler)
        listener = NetworkListener(topic=handler.topic, callback=handler, ipfs_api=self.ipfs_api)
        listener.start()
