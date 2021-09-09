from threading import Thread
from collections import defaultdict
from queue import Queue


class Listener(Thread):
    def __init__(self, topic: str, callback):
        super().__init__(daemon=True)
        self.topic = topic
        self.callback = callback

    def run(self) -> None:
        event_stream: EventStream = EventStream.get_instance()
        for event in event_stream.subscribe(topic=self.topic):
            self.callback(event)


class OneTimeListener(Thread):
    def __init__(self, topic: str, callback):
        super().__init__(daemon=True)
        self.topic = topic
        self.callback = callback

    def run(self) -> None:
        event_stream: EventStream = EventStream.get_instance()
        for event in event_stream.subscribe(topic=self.topic):
            if self.callback(event):
                break


class Event:
    def __init__(self, name, **kwargs):
        self.name = name
        self.args = kwargs

    def __str__(self):
        return f"Event(name='{self.name}', args={self.args})"


class EventStream:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise RuntimeError(f"{cls.__name__} is not initialized.")
        return cls._instance

    def __init__(self):
        self.topics = defaultdict(Queue)
        self._stop = False

        self.__class__._instance = self

    def subscribe(self, topic: str):
        topic_queue = self.topics[topic]
        while not self._stop:
            yield topic_queue.get()

    def publish(self, topic, event: Event):
        self.topics[topic].put(event)


def setup_event_stream():
    event_stream = EventStream()
    return event_stream
