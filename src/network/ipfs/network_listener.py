from threading import Thread

from .api import IpfsAPI, Message
from event_stream import Event, EventStream


class StreamClosedError(AttributeError):
    pass

TOPIC = "network"


class NetworkListener(Thread):
    def __init__(
        self,
        topic: str,
        ipfs_api: IpfsAPI,
    ):
        super().__init__(name=f"{topic} listener", daemon=True)
        self._topic = topic
        self._ipfs_api = ipfs_api
        self.event_stream: EventStream = EventStream.get_instance()

    def run(self) -> None:
        try:
            for message in self._ipfs_api.sub_to_topic(self._topic):
                message_data = message["data"]
                serialized_message: Message = Message.from_json(message_data)
                if (
                    not serialized_message.has_node_id()
                    or serialized_message.get_node_id() == self._ipfs_api.node_id
                ):
                    # ignore self messages
                    continue
                try:
                    self.event_stream.publish(TOPIC, Event(TOPIC+"-"+self._topic, message=serialized_message))
                except Exception as EX:
                    print(type(EX), EX)
        except AttributeError:
            print(f"[X] - Subscription Stream {self._topic} has bin closed")
