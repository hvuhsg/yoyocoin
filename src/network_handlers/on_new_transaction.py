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
from ipfs import Node, MessageInterface, Message


class NewTransactionHandler:
    topic = "new-transaction"

    def __init__(self, node: Node):
        self.node = node

    def validate(self, message: Message):
        return message.has_cid() and "hash" in message.meta and "nonce" in message.meta

    def message_is_relevant(self, message: Message) -> bool:
        transaction_hash = message.meta.get("hash")
        transaction_nonce = message.meta.get("nonce")
        # TODO: check if transaction is all ready stored
        # TODO: check the transaction nonce is relevant (still valid)
        return True

    def load_transaction(self, message: MessageInterface) -> dict:
        cid = message.get_cid()
        return self.node.load_cid(cid)

    def parse_transaction(self, transaction_dict: dict) -> Transaction:
        return Transaction.from_dict(**transaction_dict)

    def __call__(self, message: MessageInterface):
        if not self.validate(message):
            return
        if not self.message_is_relevant(message):
            return
        transaction_dict = self.load_transaction(message)
        transaction = self.parse_transaction(transaction_dict)
        print(transaction.to_dict())
        # TODO: add transaction to transaction pool


