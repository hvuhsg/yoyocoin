from enum import Enum

from blockchain import Transaction, Blockchain

from node.blueprints.protocol import Protocol
from node.blueprints.message import Message

from .gossip_transactions_protocol import GossipTransactionsProtocol


class Routes(Enum):
    SendTransaction = 0


class AddTransactionProtocol(Protocol):

    def process(self, message: Message) -> dict:
        if Routes(message.route) == Routes.SendTransaction:
            return self.send_transaction(message)

    def send_transaction(self, message: Message):
        blockchain = Blockchain.get_main_chain()

        if "transaction" not in message.params:
            return {"Error": "transaction parameter is required"}
        transaction = message.params["transaction"]
        transaction = Transaction.from_dict(**transaction)
        blockchain.add_transaction(transaction)

        self.broadcast(GossipTransactionsProtocol.transaction_hash_gossip_message(transaction_hash=transaction.hash()))

