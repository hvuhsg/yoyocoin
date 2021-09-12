from event_stream import Event, Subscriber, EventStream
from .blockchain import Blockchain, Block, Transaction
from .exceptions import ValidationError


def add_transaction(event: Event):
    transaction = event.args["transaction"]
    if not isinstance(transaction, Transaction):
        # TODO: log error
        print(transaction)
        return
    blockchain: Blockchain = Blockchain.get_main_chain()
    blockchain.add_transaction(transaction)


def add_block(event: Event):
    block = event.args["block"]
    if not isinstance(block, Block):
        # TODO: log error
        print(block)
        return
    blockchain: Blockchain = Blockchain.get_main_chain()
    try:
        blockchain.add_block(block)
    except ValidationError:
        event_stream: EventStream = EventStream.get_instance()
        event_stream.publish(topic="invalid-network-block", event=Event(name="invalid block added"))


def add_chain(event: Event):
    chain = event.args["chain"]
    if not isinstance(chain, list):
        # TODO: log error
        return
    blockchain: Blockchain = Blockchain.get_main_chain()
    try:
        blockchain.add_chain(chain)
    except ValidationError:
        event_stream: EventStream = EventStream.get_instance()
        event_stream.publish(topic="invalid-network-block", event=Event(name="invalid block added"))


def setup_subscribers():
    new_block_listener = Subscriber(topic="new-block", callback=add_block)
    new_block_listener.start()

    new_transaction_listener = Subscriber(topic="new-transaction", callback=add_transaction)
    new_transaction_listener.start()

    new_chain_listener = Subscriber(topic="new-chain", callback=add_chain)
    new_chain_listener.start()
