from abc import ABC, abstractmethod

from node.protocols_manager import Message


class Protocol(ABC):
    name: str

    @abstractmethod
    def process(self, message: Message) -> dict:
        return NotImplemented
