"""
Handle new transaction
When new transaction is sent, the handler will execute those steps:
1. validate message
2. if transaction hash and nonce are relevant (transaction is not stored yet and nonce is valid)
3. get new transaction via cid
4. parse new transaction and verify it
4. add transaction to transaction pool
"""
from blockchain import Transaction
from network.ipfs import Node, Message
from event_stream import Event, EventStream

from .handler import Handler


class NewTransactionHandler(Handler):
    topic = "new-transaction"

    def __init__(self):
        self.node = Node.get_instance()

    def validate(self, message: Message):
        return message.has_cid() and "hash" in message.meta and "nonce" in message.meta

    def load_transaction(self, message: Message) -> dict:
        cid = message.get_cid()
        return self.node.load_cid(cid)

    def parse_transaction(self, transaction_dict: dict) -> Transaction:
        return Transaction.from_dict(**transaction_dict)

    def publish_event(self, transaction: Transaction):
        event_stream: EventStream = EventStream.get_instance()
        event_stream.publish("new-transaction", Event("network-new-transaction", transaction=transaction))

    def __call__(self, message: Message):
        super().log(message)
        if not self.validate(message):
            return
        transaction_dict = self.load_transaction(message)
        transaction = self.parse_transaction(transaction_dict)
        self.publish_event(transaction)
