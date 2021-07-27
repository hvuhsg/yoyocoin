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
        on_new_block: Callable,
        on_new_transaction: Callable,
        on_better_chain: Callable,
        on_transactions_request: Callable,
        on_chain_info_request: Callable,
        is_full_node: bool = True,
    ):
        if not callable(on_new_block):
            raise CallbackIsNotCallable(on_new_block)
        if not callable(on_new_transaction):
            raise CallbackIsNotCallable(on_new_transaction)
        if not callable(on_better_chain):
            raise CallbackIsNotCallable(on_better_chain)
        if not callable(on_transactions_request):
            raise CallbackIsNotCallable(on_transactions_request)
        if not callable(on_chain_info_request):
            raise CallbackIsNotCallable(on_chain_info_request)

        self.ipfs_api = IpfsAPI()

        self.is_full_node = is_full_node

        self.on_better_chain = on_better_chain
        self.on_new_block = on_new_block
        self.on_new_transaction = on_new_transaction
        self.on_transactions_request = on_transactions_request
        self.on_chain_info_request = on_chain_info_request

        self.setup_listeners()

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
        listener = NetworkListener(topic=handler.topic, callback=handler, ipfs_api=self.ipfs_api)
        listener.start()

    def setup_listeners(self):
        # Public listeners
        on_chain_request = NetworkListener(
            topic="chain", callback=self.on_chain_info_request, ipfs_api=self.ipfs_api
        )
        on_transactions_request = NetworkListener(
            topic="transaction",
            callback=self.on_transactions_request,
            ipfs_api=self.ipfs_api,
        )
        on_new_block_listener = NetworkListener(
            topic="new-block", callback=self.on_new_block, ipfs_api=self.ipfs_api
        )
        on_new_transaction_listener = NetworkListener(
            topic="new-transaction",
            callback=self.on_new_transaction,
            ipfs_api=self.ipfs_api,
        )
        on_better_chain_listener = NetworkListener(
            topic="chain", callback=self.on_better_chain, ipfs_api=self.ipfs_api
        )

        on_chain_request.start()
        on_transactions_request.start()
        on_new_block_listener.start()
        on_new_transaction_listener.start()
        on_better_chain_listener.start()
