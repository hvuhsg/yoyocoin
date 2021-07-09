class Message:
    def __init__(self, protocol: str, route: str = None, params: dict = None):
        self.protocol = protocol
        self.route = route
        self.params = params

    def to_dict(self) -> dict:
        return {"protocol": self.protocol, "route": self.protocol, "params": self.params}

    @classmethod
    def from_dict(cls, message_dict: dict):
        return Message(**message_dict)
