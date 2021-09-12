from threading import Thread

from loguru import logger

from .event_stream import EventStream


class Subscriber(Thread):
    def __init__(self, topic: str, callback, offset: int = 0):
        super().__init__(daemon=True)
        self.topic = topic
        self.callback = logger.catch(callback)
        self.offset = offset

    def run(self) -> None:
        event_stream: EventStream = EventStream.get_instance()
        for event in event_stream.subscribe(topic=self.topic, offset=self.offset):
            if self.callback(event):
                break
