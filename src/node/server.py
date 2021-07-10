import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends

from .connections_manager import ConnectionManager, get_connection_manager
from .protocols_manager import ProtocolManager, get_protocol_manager

from node.blueprints.protocol import Protocol
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
            log_level: str = "info"
    ):
        self.host = host
        self.port = port
        self.log_level = log_level

        # Setup managers
        self._connections_manager = ConnectionManager(max_outbound_connections, max_inbound_connections)
        self._protocol_manager = ProtocolManager()

        # setup node
        self._register_node_protocols()

    def _register_node_protocols(self):
        self._protocol_manager.register_protocol(NodesListProtocol())

    def register_protocol(self, protocol: Protocol):
        self._protocol_manager.register_protocol(protocol)

    def run(self):
        uvicorn.run("node.server:app", host=self.host, port=self.port, log_level=self.log_level)


@app.on_event("startup")
async def startup():
    # init singletons
    NodesList()

    # start cron jobs
    OutboundConnectionsMonitor()


@app.on_event("shutdown")
async def shutdown():
    await get_connection_manager().stop()


@app.websocket("/connect_as_peer")
async def connect_to_peer(
        ws: WebSocket,
        connection_manager: ConnectionManager = Depends(get_connection_manager),
        protocol_manager: ProtocolManager = Depends(get_protocol_manager),
):
    if connection_manager.inbound_connections_is_full():
        await ws.close()
        return

    await ws.accept()
    connection_manager.new_inbound_connection(ws)

    try:
        while connection_manager.running:
            message = await ws.receive_json()
            response = protocol_manager.process_message(message)
            await ws.send_json(response)
    except WebSocketDisconnect:
        connection_manager.remove_inbound_connection(ws)
        await ws.close()

