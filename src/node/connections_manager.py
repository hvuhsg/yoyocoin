from uuid import UUID

from fastapi import WebSocket as InboundWS
from websocket import WebSocket as OutboundWS

from globals.singleton import Singleton

from node.blueprints.message import Message

__all__ = ["ConnectionManager", "get_connection_manager"]


class ConnectionManager(Singleton):
    def __init__(self, max_inbound_connections: int, max_outbound_connections: int):
        self.max_outbound_connections = max_outbound_connections
        self.max_inbound_connections = max_inbound_connections
        self.inbound_connections = {}  # {UUID: WebSocket}
        self.outbound_connections = {}  # {UUID: WebSocket}
        self.connections = {}  # {UUID: (ip, port)}

        self._event_loop = None

        self._stop = False
        super().__init__()

    @property
    def running(self):
        return not self._stop

    def set_event_loop(self, loop):
        self._event_loop = loop

    async def stop(self):
        """Stop all connections"""
        self._stop = True
        for ws in self.inbound_connections.keys():  # type: InboundWS
            await ws.close()
        for ws in self.outbound_connections.keys():  # type: OutboundWS
            ws.close()

    def new_inbound_connection(self, ws_id: UUID, ws: InboundWS, address: tuple):
        """Add new inbound connection"""
        self.inbound_connections[ws_id] = ws
        self.connections[ws_id] = address

    def new_outbound_connection(self, ws_id: UUID, ws: OutboundWS, address: tuple):
        """Add new outbound connection"""
        self.outbound_connections[ws_id] = ws
        self.connections[ws_id] = address

    def remove_inbound_connection(self, ws_id: UUID):
        """Remove inbound connection"""
        self.inbound_connections.pop(ws_id)
        self.connections.pop(ws_id)

    def remove_outbound_connection(self, ws_id: UUID):
        """Remove outbound connection"""
        self.outbound_connections.pop(ws_id)
        self.connections.pop(ws_id)

    def inbound_connections_is_full(self) -> bool:
        """Indicate if the count of inbound connections is >= max inbound connections"""
        return len(self.inbound_connections) >= self.max_inbound_connections

    def outbound_connections_is_full(self) -> bool:
        """Indicate if the count of outbound connections is >= max inbound connections"""
        return len(self.outbound_connections) >= self.max_outbound_connections

    def broadcast(self, message: Message):
        for ws in self.inbound_connections.values():  # type: InboundWS
            self._event_loop.create_task(ws.send_json(message.to_dict()))
        for ws in self.outbound_connections.values():  # type: OutboundWS
            ws.send(message.to_json())

    def send_to_node(self, node_address, message: Message):
        for uuid, address in self.connections.items():
            if address != node_address:
                continue
            if self.outbound_connections.get(uuid, None) is not None:
                ws: OutboundWS = self.outbound_connections[uuid]
                ws.send(message.to_json())
                break
            elif self.inbound_connections.get(uuid, None) is not None:
                ws: InboundWS = self.inbound_connections[uuid]
                self._event_loop.create_task(ws.send_json(message.to_dict()))
                break


def get_connection_manager() -> ConnectionManager:
    """Return's connection manager global object"""
    return ConnectionManager.get_instance()
