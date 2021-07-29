"""
Handle transactions request
if transactions request is initiated the handler will execute those steps:
1. validate message
2. get transactions
3. publish transactions and get cid
4. send the transactions cid
"""
from ipfs import Node, MessageInterface, Message

from .handler import Handler


class TransactionsRequestHandler(Handler):
    topic = "transactions-request"
    topic_response = "transactions-response"

    def __init__(self, node: Node):
        self.node = node
        self._cid = None

    def validate(self, message: MessageInterface):
        return True

    def get_transactions(self) -> dict:
        # TODO: get transactions from pool
        transactions = ["t1", "t2", "t3"]
        return {"transactions": transactions}

    def publish_transactions(self, transactions: dict) -> str:
        return self.node.create_cid(transactions)

    def send_cid_and_count(self, cid: str, count: int):
        return self.node.publish_to_topic(
            topic=self.topic_response, message=Message(cid=cid, meta={"count": count})
        )

    def __call__(self, message: Message):
        super().log(message)
        if not self.validate(message):
            return
        transactions = self.get_transactions()
        cid = self.publish_transactions(transactions)
        self.send_cid_and_count(cid, len(transactions))
