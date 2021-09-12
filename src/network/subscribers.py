from event_stream import Subscriber, Event
from blockchain import Blockchain, Block, Transaction

from .messages import SyncRequest, NewTransaction, NewBlock


def lifecycle_callback(event: Event):
    if event.name == "end-setup":
        blockchain: Blockchain = Blockchain.get_main_chain()
        SyncRequest(score=blockchain.score, length=blockchain.length).send()
        return True  # Stop listening on topic. closing subscriber


def new_block_callback(event: Event):
    if event.name == "block_created":
        block: Block = event.args["block"]
        NewBlock(block=block.to_dict(), previous_hash=block.previous_hash, index=block.index).send()


def new_transaction_callback(event: Event):
    if event.name == "transaction_created":
        transaction: Transaction = event.args["transaction"]
        NewTransaction(transaction.to_dict(), hash=transaction.hash(), nonce=transaction.nonce).send()


def invalid_network_state_callback(event: Event):
    blockchain: Blockchain = Blockchain.get_main_chain()
    SyncRequest(score=blockchain.score, length=blockchain.length).send()


def setup_subscribers():
    invalid_network_state_subscriber = Subscriber(topic="invalid-network-block", callback=invalid_network_state_callback)
    lifecycle_subscriber = Subscriber(topic="lifecycle", callback=lifecycle_callback)
    new_block_subscriber = Subscriber(topic="block-created", callback=new_block_callback)
    new_transaction_subscriber = Subscriber(topic="new-transaction", callback=new_transaction_callback)

    lifecycle_subscriber.start()
    new_block_subscriber.start()
    new_transaction_subscriber.start()
    invalid_network_state_subscriber.start()
