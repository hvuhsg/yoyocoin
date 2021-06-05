from enum import Enum
from hashlib import sha256
from json import dumps
from base64 import b64decode

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
        sender_wallet_address: str = None,
        **kwargs
    ):
        self.payload = payload
        self.message_type = message_type
        self.ttl = ttl
        self.signature = signature
        self.route = route
        self.from_wallet_address = sender_wallet_address
        self.valid = True
        self.unsupported = kwargs
        self.process()

    @property
    def hash(self) -> str:
        payload_json = dumps(self.payload, sort_keys=True)
        return sha256(payload_json.encode()).hexdigest()

    def process(self):
        self.ttl -= 1
        if not self.validate():
            self.valid = False

    def validate(self):
        # TODO: validate ttl max size and more
        return self.validate_signature()

    def is_alive(self):
        return self.ttl > 0 and self.valid

    def validate_signature(self) -> bool:
        return True  # TODO: validate signature

    def to_dict(self):
        return {
            "payload": self.payload,
            "metadata": {
                "ttl": self.ttl,
                "message_type": self.message_type,
                "signature": self.signature,
                "route": self.route,
                "sender_wallet_address": self.from_wallet_address,
            },
        }

    @classmethod
    def from_dict(cls, data):
        metadata = data["metadata"]
        payload = data["payload"]
        return cls(payload, **metadata)
