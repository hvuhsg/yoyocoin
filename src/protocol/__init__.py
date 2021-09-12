from event_stream import Subscriber, Event

from .on_transactions_request import TransactionsRequestHandler
from .on_new_block import NewBlockHandler
from .on_transactions_response import TransactionsHandler
from .on_new_transaction import NewTransactionHandler
from .on_chain_info import ChainInfoHandler
from .on_chain_info_request import ChainInfoRequestHandler


__all__ = ["setup_protocol"]


class Protocol:
    def __init__(self):
        self.new_block_protocol = NewBlockHandler()
        self.new_transaction_protocol = NewTransactionHandler()
        self.chain_request_protocol = ChainInfoRequestHandler()
        self.chain_response_protocol = ChainInfoHandler()

    def network_callback(self, event: Event):
        if event.name == "network-new-block":
            self.new_block_protocol(event.args["message"])
        if event.name == "network-new-transaction":
            self.new_transaction_protocol(event.args["message"])
        if event.name == "network-chain-request":
            self.chain_request_protocol(event.args["message"])
        if event.name == "network-chain-response":
            self.chain_response_protocol(event.args["message"])


def setup_protocol():
    protocol = Protocol()
    network_listener = Subscriber(topic="network", callback=protocol.network_callback)
    network_listener.start()
