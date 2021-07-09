from threading import Thread
from json import loads

import websocket


from .protocols_manager import ProtocolManager, get_protocol_manager
from .connections_manager import ConnectionManager, get_connection_manager


def create_connection(address: tuple):
    ws = websocket.WebSocket()
    ws.connect(f"ws://{address[0]}:{address[1]}/connect_as_peer", timeout=10)
    t = Thread(target=handle_connection, args=(ws, ))
    t.daemon = True
    t.start()


def handle_connection(ws: websocket.WebSocket):
    protocol_manager: ProtocolManager = get_protocol_manager()
    connection_manager: ConnectionManager = get_connection_manager()
    connection_manager.new_inbound_connection(ws)

    try:
        while connection_manager.running:
            raw_message = ws.recv()
            message = loads(raw_message)
            response = protocol_manager.process_message(message)
            ws.send(response)
    except websocket.WebSocketConnectionClosedException:
        connection_manager.remove_outbound_connection(ws)
        ws.close()
