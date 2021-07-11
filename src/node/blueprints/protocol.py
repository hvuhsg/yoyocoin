from abc import ABC, abstractmethod

from .message import Message
from ..connections_manager import ConnectionManager, get_connection_manager


class Protocol(ABC):
    name: str

    def __init__(self):
        self.connection_manager: ConnectionManager = get_connection_manager()

    @abstractmethod
    def process(self, message: Message) -> dict:
        return NotImplemented

    def broadcast(self, message: Message):
        self.connection_manager.broadcast(message)
