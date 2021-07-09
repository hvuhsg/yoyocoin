from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends

from .connections_manager import ConnectionManager, get_connection_manager
from .protocols_manager import ProtocolManager, get_protocol_manager

from .cronjobs import OutboundConnectionsMonitor, LotteryManager
from .protocols import NodesListProtocol, LotteryProtocol

app = FastAPI()


@app.on_event("startup")
async def startup():
    # Init singletons
    ConnectionManager(max_inbound_connections=10, max_outbound_connections=10)

    pm = ProtocolManager()
    pm.register_protocol(LotteryProtocol())
    pm.register_protocol(NodesListProtocol())

    # start monitor
    OutboundConnectionsMonitor()

    # start lottery manager
    LotteryManager()


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

