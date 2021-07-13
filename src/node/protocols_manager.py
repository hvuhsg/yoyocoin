from typing import Dict

from globals.singleton import Singleton
from node.blueprints.protocol import Protocol
from node.blueprints.message import Message, SerializationError


class ProtocolManager(Singleton):
    def __init__(self, protocols=None):
        if protocols is None:
            protocols = {}

        self.sub_nodes_protocols: Dict[str, Protocol] = {}  # {protocol_name: protocol_object}
        self.protocols: Dict[str, Protocol] = protocols  # {protocol_name: protocol_object}

        super().__init__()

    def register_protocol(self, protocol: Protocol):
        self.protocols[protocol.name] = protocol

    def register_sub_node_protocol(self, protocol: Protocol):
        self.sub_nodes_protocols[protocol.name] = protocol

    def process_sub_node_message(self, message: dict) -> Message:
        message = self._serialize_message(message)
        protocol_name = message.protocol
        if protocol_name not in self.sub_nodes_protocols:
            return {"Error": "Protocol not found"}
        result = self.sub_nodes_protocols[protocol_name].process(message)
        return result

    def _serialize_message(self, message: dict) -> Message:
        # Serialize message
        try:
            message = Message.from_dict(message)
        except TypeError as TE:
            raise SerializationError(error="message serialize error", message=message)
        return message

    def process_message(self, message: dict) -> Message:
        """Process message and return's the result"""
        message = self._serialize_message(message)
        protocol_name = message.protocol
        if protocol_name not in self.protocols:
            return {"Error": "Protocol not found"}

        result = self.protocols[protocol_name].process(message)
        return result


def get_protocol_manager() -> ProtocolManager:
    return ProtocolManager.get_instance()
