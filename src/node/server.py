from asyncio import get_event_loop
from uuid import uuid4

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends

from .connections_manager import ConnectionManager, get_connection_manager
from .protocols_manager import ProtocolManager, get_protocol_manager

from .blueprints.protocol import Protocol
from .blueprints.message import Message
from .protocols.nodes_list_protocols import NodesListProtocol
from .cronjobs import OutboundConnectionsMonitor
from .nodes_list import NodesList

app = FastAPI()


class Node:
    def __init__(
            self,
            host: str,
            port: int,
            max_outbound_connections: int,
            max_inbound_connections: int,
            max_sub_nodes_connections: int,
            log_level: str = "info"
    ):
        self.host = host
        self.port = port
        self.log_level = log_level

        # Setup managers
        self._connections_manager = ConnectionManager(
            max_outbound_connections,
            max_inbound_connections,
            max_sub_nodes_connections,
        )
        self._protocol_manager = ProtocolManager()

        # setup node
        self._register_node_protocols()

    def _register_node_protocols(self):
        self._protocol_manager.register_protocol(NodesListProtocol())

    def register_protocol(self, protocol: Protocol):
        self._protocol_manager.register_protocol(protocol)

    def register_sub_node_protocol(self, protocol: Protocol):
        self._protocol_manager.register_sub_node_protocol(protocol)

    def run(self):
        uvicorn.run("node.server:app", host=self.host, port=self.port, log_level=self.log_level)


@app.on_event("startup")
async def startup():
    connections_manager: ConnectionManager = get_connection_manager()
    connections_manager.set_event_loop(get_event_loop())

    # init singletons
    NodesList()

    # start cron jobs
    OutboundConnectionsMonitor()


@app.on_event("shutdown")
async def shutdown():
    await get_connection_manager().stop()


@app.websocket("/connect_as_sub_node")
async def connect_as_sub_node(
    ws: WebSocket,
    connection_manager: ConnectionManager = Depends(get_connection_manager),
    protocol_manager: ProtocolManager = Depends(get_protocol_manager),
):
    if connection_manager.sub_connections_is_full():
        await ws.close()
        return
    await ws.accept()
    ws_id = uuid4()
    connection_manager.new_sub_node_connection(ws_id, ws)

    try:
        message = await ws.receive_json()
        result = protocol_manager.process_sub_node_message(message)
        if result:
            await ws.send_json(result.to_dict())
    except WebSocketDisconnect:
        connection_manager.remove_sub_node_connection(ws_id)
        await ws.close()


@app.websocket("/connect_as_peer")
async def connect_to_peer(
        host: str,
        port: int,
        ws: WebSocket,
        connection_manager: ConnectionManager = Depends(get_connection_manager),
        protocol_manager: ProtocolManager = Depends(get_protocol_manager),
):
    if connection_manager.inbound_connections_is_full():
        await ws.close()
        return

    await ws.accept()
    ws_id = uuid4()
    if host == "0.0.0.0":
        host = ws.client.host
    address = (host, port)
    connection_manager.new_inbound_connection(ws_id, ws, address)

    try:
        while connection_manager.running:
            message = await ws.receive_json()
            response: Message = protocol_manager.process_message(message)
            if response:
                await ws.send_json(response.to_dict())
    except WebSocketDisconnect:
        connection_manager.remove_inbound_connection(ws_id)
        await ws.close()

