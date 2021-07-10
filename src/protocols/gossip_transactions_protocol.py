from enum import Enum, auto

from node.blueprints.protocol import Protocol
from node.blueprints.message import Message


class Routes(Enum):
    TxHash = auto()
    TxValue = auto()


class GossipTransactionsProtocol(Protocol):
    name: str = "GossipTransactions"

    def process(self, message: Message) -> dict:
        if message.route == Routes.TxHash:
            pass  # Check storage for transaction (if not exist request transaction value)
        elif message.route == Routes.TxValue:
            pass  # Return transaction value if exist
