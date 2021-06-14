from enum import Enum
from hashlib import sha256
from json import dumps
from base64 import b64decode

from .constants import MAX_TTL


__all__ = ["MessageType", "Message", "Route"]


class MessageType(Enum):
    DIRECT = 0
    BROADCAST = 1


class Route(Enum):
    NewTX = 0
    NewBlock = 1
    ReportNode = 2
    ForgeBlock = 3
    PeersList = 4
    ChainHistory = 5
    Test = 6
    OTHER = 100


class Message:
    def __init__(
        self,
        payload: dict,
        route: Route,
        message_type: MessageType,
        ttl: int = 0,
        signature: str = None,
        from_wallet_address: str = None,
        **kwargs
    ):
        if type(message_type) is int:
            message_type = MessageType(message_type)
        if type(route) is int:
            route = Route(route)
        self.payload = payload
        self.message_type = message_type
        self.ttl = ttl
        self.signature = signature
        self.route = route
        self.from_wallet_address = from_wallet_address
        self.valid = True
        self.unsupported = kwargs
        self.process()

    def process(self):
        self.ttl -= 1
        if not self.validate():
            self.valid = False

    @property
    def hash(self) -> str:
        payload_json = dumps(self.payload, sort_keys=True)
        return sha256(payload_json.encode()).hexdigest()

    def broadcast_forward(self):
        return self.is_alive() and self.message_type == MessageType.BROADCAST

    def validate(self):
        # TODO: validate ttl max size and more
        if not self.validate_signature():
            return False
        if self.ttl > MAX_TTL:
            return False
        return True

    def is_alive(self):
        return self.ttl > 0 and self.valid

    def validate_signature(self) -> bool:
        return True  # TODO: validate signature

    def to_dict(self):
        return {
            "payload": self.payload,
            "metadata": {
                "ttl": self.ttl,
                "message_type": self.message_type.value,
                "signature": self.signature,
                "route": self.route.value,
                "sender_wallet_address": self.from_wallet_address,
                "unsupported": self.unsupported,
            },
        }

    @classmethod
    def from_dict(cls, data):
        metadata = data["metadata"]
        payload = data["payload"]
        return cls(payload, **metadata)

    @classmethod
    def test_message(cls, data: dict, from_wallet_address):
        return cls(
            payload=data,
            route=Route.Test,
            message_type=MessageType.BROADCAST,
            ttl=MAX_TTL,
            from_wallet_address=from_wallet_address,
        )

    @classmethod
    def new_transaction(cls, data: dict, from_wallet_address):
        return cls(
            payload=data,
            route=Route.NewTX,
            message_type=MessageType.BROADCAST,
            ttl=MAX_TTL,
            from_wallet_address=from_wallet_address,
        )

    @classmethod
    def new_block(cls, data: dict, from_wallet_address):
        return cls(
            payload=data,
            route=Route.NewBlock,
            message_type=MessageType.BROADCAST,
            ttl=MAX_TTL,
            from_wallet_address=from_wallet_address,
        )
