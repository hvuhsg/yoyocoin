from enum import Enum

from blockchain import Blockchain, Transaction

from node.blueprints.protocol import Protocol
from node.blueprints.message import Message


class Routes(Enum):
    TxHash = 0
    TxValueRequest = 1
    TxValueResponse = 2


class GossipTransactionsProtocol(Protocol):
    name: str = "GossipTransactions"

    def process(self, message: Message) -> dict:
        if Routes(message.route) == Routes.TxHash:
            return self.on_transaction_hash_gossip(message)
            # Check storage for transaction (if not exist request transaction value)
        elif Routes(message.route) == Routes.TxValueRequest:
            return self.on_transaction_value_request(message)
            # Return transaction value if exist
        elif Routes(message.route) == Routes.TxValueResponse:
            return self.on_transaction_value_response(message)
            # Validate transaction and save it

    @classmethod
    def transaction_hash_gossip_message(cls, transaction_hash: str) -> Message:
        return Message(protocol=cls.name, route=Routes.TxHash, params={"transaction_hash": transaction_hash})

    def on_transaction_hash_gossip(self, message: Message):
        blockchain = Blockchain.get_main_chain()
        tx_hash = message.params["transaction_hash"]
        if tx_hash in blockchain.current_transactions:
            return
        return Message(protocol=self.name, route=Routes.TxValueRequest, params={"transaction_hash": tx_hash})

    def on_transaction_value_request(self, message: Message):
        blockchain = Blockchain.get_main_chain()
        tx_hash = message.params["transaction_hash"]

        if tx_hash not in blockchain.current_transactions:
            return
        transaction = blockchain.current_transactions[tx_hash]
        return Message(protocol=self.name, route=Routes.TxValue, params={"transaction": transaction.to_dict()})

    def on_transaction_value_response(self, message: Message):
        blockchain = Blockchain.get_main_chain()
        tx = message.params["transaction"]
        transaction = Transaction.from_dict(**tx)
        transaction.validate(blockchain.state, is_test_net=blockchain.is_test_net)
        blockchain.add_transaction(transaction)
