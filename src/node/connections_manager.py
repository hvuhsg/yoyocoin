from fastapi import WebSocket as InboundWS
from websocket import WebSocket as OutboundWS

from globals.singleton import Singleton

from node.blueprints.message import Message

__all__ = ["ConnectionManager", "get_connection_manager"]


class ConnectionManager(Singleton):
    def __init__(self, max_inbound_connections: int, max_outbound_connections: int):
        self.max_outbound_connections = max_outbound_connections
        self.max_inbound_connections = max_inbound_connections
        self.inbound_connections = {}  # {WebSocket: dict<connection data>}
        self.outbound_connections = {}  # {WebSocket: dict<connection_data>}

        self._stop = False
        super().__init__()

    @property
    def running(self):
        return not self._stop

    async def stop(self):
        """Stop all connections"""
        self._stop = True
        for ws in self.inbound_connections.keys():  # type: InboundWS
            await ws.close()
        for ws in self.outbound_connections.keys():  # type: OutboundWS
            ws.close()

    def new_inbound_connection(self, ws: InboundWS):
        """Add new inbound connection"""
        self.inbound_connections[ws] = {}

    def new_outbound_connection(self, ws: OutboundWS):
        """Add new outbound connection"""
        self.inbound_connections[ws] = {}

    def remove_inbound_connection(self, ws: InboundWS):
        """Remove inbound connection"""
        self.inbound_connections.pop(ws)

    def remove_outbound_connection(self, ws: OutboundWS):
        """Remove outbound connection"""
        self.outbound_connections.pop(ws)

    def inbound_connections_is_full(self) -> bool:
        """Indicate if the count of inbound connections is >= max inbound connections"""
        return len(self.inbound_connections) >= self.max_inbound_connections

    def outbound_connections_is_full(self) -> bool:
        """Indicate if the count of outbound connections is >= max inbound connections"""
        return len(self.outbound_connections) >= self.max_outbound_connections

    async def broadcast(self, message: Message):
        for ws in self.inbound_connections.keys():  # type: InboundWS
            await ws.send_json(message.to_dict())
        for ws in self.outbound_connections.keys():  # type: OutboundWS
            ws.send(message.to_dict())


def get_connection_manager() -> ConnectionManager:
    """Return's connection manager global object"""
    return ConnectionManager.get_instance()
