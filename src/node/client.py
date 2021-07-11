from threading import Thread
from json import loads
from uuid import uuid4

import websocket

from config import PORT
from .blueprints.message import Message
from .protocols_manager import ProtocolManager, get_protocol_manager
from .connections_manager import ConnectionManager, get_connection_manager


def create_connection(address: tuple):
    ws = websocket.WebSocket()
    try:
        ws.connect(f"ws://{address[0]}:{address[1]}/connect_as_peer?host=0.0.0.0&port={PORT}")
    except ConnectionError:
        return
    t = Thread(target=handle_connection, args=(ws, address))
    t.daemon = True
    t.start()


def handle_connection(ws: websocket.WebSocket, address: tuple):
    protocol_manager: ProtocolManager = get_protocol_manager()
    connection_manager: ConnectionManager = get_connection_manager()
    ws_id = uuid4()
    connection_manager.new_outbound_connection(ws_id, ws, address)

    try:
        while connection_manager.running:
            raw_message = ws.recv()
            message = loads(raw_message)
            response: Message = protocol_manager.process_message(message)
            if response:
                ws.send(response.to_json())
    except websocket.WebSocketConnectionClosedException:
        connection_manager.remove_outbound_connection(ws_id)
