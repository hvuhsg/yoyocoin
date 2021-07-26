from threading import Thread
from api import IpfsAPI, Message, MessageType, message_serializer


class NetworkListener(Thread):
    def __init__(self, topic: str, callback, ipfs_api: IpfsAPI, serializer=message_serializer):
        super().__init__(name=f"{topic} listener", daemon=False)
        self._topic = topic
        self._callback = callback
        self._ipfs_api = ipfs_api

        self._serializer = serializer

    def run(self) -> None:
        for message in self._ipfs_api.sub_to_topic(self._topic):
            message_data = message["data"]
            serialized_message = self._serializer(message_data)
            try:
                self._callback(serialized_message, self._topic)
            except Exception as EX:
                print(type(EX), EX)
