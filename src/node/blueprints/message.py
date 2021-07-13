from json import dumps


class SerializationError(Exception):
    def __init__(self, error, message, *args):
        self.error = error
        self.message = message
        super().__init__(args)


class Message:
    def __init__(self, protocol: str, route: str = None, params: dict = None):
        self.protocol = protocol
        self.route = route
        self.params = params

    def to_dict(self) -> dict:
        return {"protocol": self.protocol, "route": self.route, "params": self.params}

    def to_json(self) -> str:
        return dumps(self.to_dict())

    @classmethod
    def from_dict(cls, message_dict: dict):
        return Message(**message_dict)

    def __repr__(self):
        return f"Message(protocol={self.protocol}, route={self.route}, params={self.params})"
