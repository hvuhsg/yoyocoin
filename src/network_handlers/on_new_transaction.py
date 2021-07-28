"""
Handle new transaction
When new transaction is sent, the handler will execute those steps:
1. validate message
2. if transaction hash and nonce are relevant (transaction is not stored yet and nonce is valid)
3. get new transaction via cid
4. parse new transaction and verify it
4. add transaction to transaction pool
"""
from blockchain import Transaction, Blockchain
from ipfs import Node, MessageInterface, Message

from .handler import Handler


class NewTransactionHandler(Handler):
    topic = "new-transaction"

    def __init__(self, node: Node):
        self.node = node

    def validate(self, message: Message):
        return message.has_cid() and "hash" in message.meta and "nonce" in message.meta

    def message_is_relevant(self, message: Message) -> bool:
        blockchain: Blockchain = Blockchain.get_main_chain()
        transaction_hash = message.meta.get("hash")
        transaction_nonce = message.meta.get("nonce")
        # TODO: check the transaction nonce is relevant (still valid)

        transaction_not_saved = transaction_hash not in blockchain.current_transactions
        return transaction_not_saved

    def load_transaction(self, message: MessageInterface) -> dict:
        cid = message.get_cid()
        return self.node.load_cid(cid)

    def parse_transaction(self, transaction_dict: dict) -> Transaction:
        return Transaction.from_dict(**transaction_dict)

    def save_transaction_to_pool(self, transaction: Transaction):
        blockchain: Blockchain = Blockchain.get_main_chain()
        blockchain.add_transaction(transaction)

    def __call__(self, message: MessageInterface):
        super().log(message)
        if not self.validate(message):
            return
        if not self.message_is_relevant(message):
            return
        transaction_dict = self.load_transaction(message)
        transaction = self.parse_transaction(transaction_dict)
        self.save_transaction_to_pool(transaction)


