from enum import Enum
from hashlib import sha256
from json import dumps

from .constants import MAX_TTL


__all__ = ["MessageType", "Message", "Route", "MessageDirection"]


class MessageDirection(Enum):
    REQUEST = 0
    RESPONSE = 1


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
    ChainSummery = 6
    Test = 7
    OTHER = 100


class Message:
    def __init__(
        self,
        payload: dict,
        route: Route,
        message_type: MessageType,
        message_direction: MessageDirection,
        ttl: int = 0,
        signature: str = None,
        node_address: str = None,
        **kwargs
    ):
        if type(message_type) is int:
            message_type = MessageType(message_type)
        if type(message_direction) is int:
            message_direction = MessageDirection(message_direction)
        if type(route) is int:
            route = Route(route)

        self.node_address = node_address
        self.signature = signature

        self.ttl = ttl
        self.message_direction = message_direction
        self.message_type = message_type
        self.route = route

        self.payload = payload
        self.valid = True
        self.unsupported = kwargs

        self.process()

    def process(self):
        if self.message_type == MessageType.BROADCAST:
            self.ttl -= 1
        if not self.validate():
            self.valid = False

    @property
    def hash(self) -> str:
        payload_json = dumps(self.payload, sort_keys=True)
        return sha256(payload_json.encode()).hexdigest()

    def broadcast_forward(self):
        return self.valid and self.message_type == MessageType.BROADCAST

    def validate(self):
        # TODO: validate ttl max size and more
        if not self.validate_signature():
            return False
        if self.message_type == MessageType.BROADCAST and self.ttl > MAX_TTL:
            return False
        if self.message_type == MessageType.BROADCAST and self.ttl < 0:
            return False
        return True

    def validate_signature(self) -> bool:
        return True  # TODO: validate signature

    def to_dict(self):
        return {
            "payload": self.payload,
            "metadata": {
                "node_address": self.node_address,
                "signature": self.signature,
                "ttl": self.ttl,
                "message_type": self.message_type.value,
                "message_direction": self.message_direction.value,
                "route": self.route.value,
                "unsupported": self.unsupported,
            },
        }

    def sign(self, private_address):
        pass

    @classmethod
    def from_dict(cls, data):
        metadata = data["metadata"]
        payload = data["payload"]
        return cls(payload, **metadata)
