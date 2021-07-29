from typing import Callable
from threading import Thread
from .api import IpfsAPI, MessageInterface, Message


class StreamClosedError(AttributeError):
    pass


class NetworkListener(Thread):
    def __init__(
            self,
            topic: str,
            callback: Callable[[MessageInterface], None],
            ipfs_api: IpfsAPI,
    ):
        super().__init__(name=f"{topic} listener", daemon=False)
        self._topic = topic
        self._callback = callback
        self._ipfs_api = ipfs_api

    def run(self) -> None:
        try:
            for message in self._ipfs_api.sub_to_topic(self._topic):
                message_data = message["data"]
                serialized_message: MessageInterface = Message.from_json(message_data)
                if (
                        not serialized_message.has_node_id()
                        or serialized_message.get_node_id() == self._ipfs_api.node_id
                ):
                    # ignore self messages
                    continue
                try:
                    self._callback(serialized_message)
                except Exception as EX:
                    print(type(EX), EX)
        except AttributeError:
            print(f"[X] - Subscription Stream {self._topic} has bin closed")
