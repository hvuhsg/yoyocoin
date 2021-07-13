from enum import Enum
from node.blueprints.protocol import Protocol
from node.blueprints.message import Message

from blockchain import Blockchain


class Routes(Enum):
    GetWalletBalanceRequest = 0
    GetWalletBalanceResponse = 1


class WalletStateProtocol(Protocol):
    name: str = "WalletStateProtocol"

    def process(self, message: Message) -> dict:
        if Routes(message.route) == Routes.GetWalletBalanceRequest:
            return self.return_wallet_balance(message)

    def return_wallet_balance(self, message: Message):
        blockchain: Blockchain = Blockchain.get_main_chain()
        if "wallet_address" not in message.params:
            return
        if message.params["wallet_address"] not in blockchain.state.wallets:
            return {"Error": "No wallet found"}
        return Message(
            protocol=self.__class__.name,
            route=Routes.GetWalletBalanceResponse.value,
            params={
                "wallet_address": message.params["wallet_address"],
                "balance": blockchain.state.wallets[message.params["wallet_address"]]["balance"]
            }
        )
