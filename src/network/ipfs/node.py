import json

from config import Config
from .api import IpfsAPI, Message
from .network_listener import NetworkListener


NETWORK_TOPICS = [
    "chain-response",
    "chain-request",
    "new-block",
    "new-transaction",
    "transactions-request",
    "transactions-response",

]


class CallbackIsNotCallable(TypeError):
    def __init__(self, non_callable):
        self.non_callable = non_callable

    def __str__(self):
        return f"The object {self.non_callable} is not callable!"


class Node:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise RuntimeError(f"{cls.__name__} is not initialized yet!")
        return cls._instance

    def __init__(self):
        self.ipfs_api = IpfsAPI(host=Config.IPFS_HOST, port=Config.IPFS_PORT)

        self.__class__._instance = self

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

    def add_listener(self, topic: str):
        listener = NetworkListener(topic=topic, ipfs_api=self.ipfs_api)
        listener.start()

    def remove_listener(self, topic: str):
        self.ipfs_api.close_stream(topic)

    def close(self):
        self.ipfs_api.close()


def setup_node():
    node = Node()
    for network_topic in NETWORK_TOPICS:
        node.add_listener(network_topic)
