from typing import Callable
from threading import Thread
from api import IpfsAPI, MessageInterface, message_serializer


class NetworkListener(Thread):
    def __init__(
            self, topic: str,
            callback: Callable[[MessageInterface], None],
            ipfs_api: IpfsAPI,
            serializer: Callable[[dict], MessageInterface] = message_serializer
    ):
        super().__init__(name=f"{topic} listener", daemon=False)
        self._topic = topic
        self._callback = callback
        self._ipfs_api = ipfs_api

        self._serializer = serializer

    def run(self) -> None:
        for message in self._ipfs_api.sub_to_topic(self._topic):
            message_data = message["data"]
            serialized_message: MessageInterface = self._serializer(message_data)
            if serialized_message.has_node_id and serialized_message.get_node_id() == self._ipfs_api.node_id:
                # ignore self messages
                continue
            try:
                self._callback(serialized_message)
            except Exception as EX:
                print(type(EX), EX)
