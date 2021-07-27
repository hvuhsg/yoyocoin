"""
Handle transactions response
if transaction response is sent, the handler will execute those steps:
1. validate message
3. get transactions via cid
4. add transactions to pool (validated on insertion)
"""
from ipfs import Node, MessageInterface


class TransactionsHandler:
    topic = "transactions-response"

    def __init__(self, node: Node):
        self.node = node

    def validate(self, message: MessageInterface):
        return True

    def message_is_relevant(self, message: MessageInterface) -> bool:
        return message.has_cid()

    def load_transactions(self, message: MessageInterface) -> dict:
        cid = message.get_cid()
        return self.node.load_cid(cid)

    def __call__(self, message: MessageInterface):
        if not self.validate(message):
            return
        if not self.message_is_relevant(message):
            return
        transactions = self.load_transactions(message)
        print(transactions)
        # TODO: update transactions pool


