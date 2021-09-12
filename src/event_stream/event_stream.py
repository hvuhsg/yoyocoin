from collections import defaultdict

from .multi_subscribers_queue import MultiSubscribersQueue
from .event import Event


class EventStream:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise RuntimeError(f"{cls.__name__} is not initialized.")
        return cls._instance

    def __init__(self):
        if self.__class__._instance is not None:
            raise RuntimeError("Singleton can be initialized once! (use get_instance()")
        self.topics = defaultdict(MultiSubscribersQueue)
        self._stop = False

        self.__class__._instance = self

    def subscribe(self, topic: str, offset: int):
        topic_queue = self.topics[topic]
        while not self._stop:
            yield topic_queue.get(offset)
            offset += 1

    def publish(self, topic, event: Event):
        self.topics[topic].put(event)

    def stop(self):
        self._stop = True


def setup_event_stream():
    event_stream = EventStream()
    return event_stream
