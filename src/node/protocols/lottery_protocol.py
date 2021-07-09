from enum import Enum, auto

from blockchain import Block

from ..cronjobs.lottery_manager import LotteryManager
from ..blueprints.protocol import Protocol
from ..blueprints.message import Message


class Routes(Enum):
    NewBlock = auto()


class LotteryProtocol(Protocol):
    name: str = "LotteryProtocol"

    def process(self, message: Message) -> dict:
        lottery_manager: LotteryManager = LotteryManager.get_instance()

        if Routes(message.route) == Routes.NewBlock:
            if "block" not in message.params:
                return {"Error": "block is required"}
            block = message.params["block"]
            block = Block.from_dict(**block)
            lottery_manager.check_lottery_block(block)

    @staticmethod
    def new_block(self, block: Block) -> Message:
        return Message.from_dict({
            "protocol": self.__class__.name,
            "route": Routes.NewBlock.value,
            "params": {"block": block.to_dict()}
        })
