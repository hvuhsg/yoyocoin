from .message import Route, Message, MessageType, MessageDirection
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

        self.__class__._instance = self

    def new_transaction(self, data: dict):
        return self._new_message(data=data, is_broadcast=True, route=Route.NewTX, direction=MessageDirection.REQUEST)

    def new_block(self, data: dict):
        return self._new_message(data=data, is_broadcast=True, route=Route.NewBlock, direction=MessageDirection.REQUEST)

    def test_direct(self, data: dict):
        return self._new_message(data=data, is_broadcast=False, route=Route.Test, direction=MessageDirection.REQUEST)

    def test_broadcast(self, data: dict):
        return self._new_message(data=data, is_broadcast=True, route=Route.Test, direction=MessageDirection.REQUEST)

    def get_peer_list(self, data: dict):
        return self._new_message(data=data, is_broadcast=True, route=Route.PeersList, direction=MessageDirection.REQUEST)

    def get_chain_history(self, data: dict):
        return self._new_message(data=data, is_broadcast=True, route=Route.ChainHistory, direction=MessageDirection.REQUEST)

    def get_chain_info(self, data: dict):
        return self._new_message(data=data, is_broadcast=True, route=Route.ChainSummery,
                                 direction=MessageDirection.REQUEST)

    def route_response(self, data: dict, route: Route):
        return self._new_message(data, is_broadcast=False, route=route, direction=MessageDirection.RESPONSE)

    def _new_message(self, data: dict, is_broadcast: bool, route: Route, direction: MessageDirection):
        m = Message(
            payload=data,
            message_type=MessageType.BROADCAST if is_broadcast else MessageType.DIRECT,
            message_direction=direction,
            route=route,
            ttl=MAX_TTL if is_broadcast else None,
            node_address=self.public_address,
        )
        m.sign(self.private_address)
        return m
