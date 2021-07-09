from globals.singleton import Singleton
from .blueprints.message import Message
from .blueprints.protocol import Protocol


class ProtocolManager(Singleton):
    def __init__(self, protocols=None):
        if protocols is None:
            protocols = {}

        self.protocols = protocols  # {protocol_name: protocol_object}

        super().__init__()

    def register_protocol(self, protocol: Protocol):
        self.protocols[protocol.name] = protocol

    def process_message(self, message: dict) -> dict:
        """Process message and return's the result"""

        # Serialize message
        try:
            message = Message.from_dict(message)
        except TypeError as TE:
            return {"Error": "message serialize error", "error_message": str(TE)}

        protocol_name = message.protocol
        if protocol_name not in self.protocols:
            return {"Error": "Protocol not found"}

        result = self.protocols[protocol_name].process(message)
        return result


def get_protocol_manager() -> ProtocolManager:
    return ProtocolManager.get_instance()
