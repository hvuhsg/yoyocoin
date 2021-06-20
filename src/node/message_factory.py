from .message import Route, Message, MessageType
from .constants import MAX_TTL


class MessageFactory:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise ValueError(cls.__name__ + " is not initiated yet.")
        return cls._instance

    def __init__(self, node_pub_address, node_pri_address):
        self.public_address = node_pub_address
        self.private_address = node_pri_address

    def new_transaction(self, data: dict):
        return self._new_message(data=data, is_broadcast=True, route=Route.NewTX)

    def new_block(self, data: dict):
        return self._new_message(data=data, is_broadcast=True, route=Route.NewBlock)

    def test_direct(self, data: dict):
        return self._new_message(data=data, is_broadcast=False, route=Route.Test)

    def test_broadcast(self, data: dict):
        return self._new_message(data=data, is_broadcast=True, route=Route.Test)

    def get_peer_list(self, data: dict):
        return self._new_message(data=data, is_broadcast=True, route=Route.PeersList)

    def get_chain_history(self, data: dict):
        return self._new_message(data=data, is_broadcast=True, route=Route.ChainHistory)

    def _new_message(self, data: dict, is_broadcast: bool, route: Route):
        m = Message(
            payload=data,
            message_type=MessageType.BROADCAST if is_broadcast else MessageType.DIRECT,
            route=route,
            ttl=MAX_TTL if is_broadcast else None,
            node_address=self.public_address,
        )
        m.sign(self.private_address)
        return m
