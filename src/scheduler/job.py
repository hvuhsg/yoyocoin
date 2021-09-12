from threading import Thread
from datetime import datetime, timedelta

from loguru import logger

from event_stream import EventStream, Event


class Job:
    def __init__(self, func, name, interval, sync, run_thread: bool, offset: int):
        self.func = func
        self.name = name
        self.interval = interval
        self.sync = sync
        self.run_thread = run_thread
        self.offset = offset
        self.last_run = datetime.utcnow()

    def is_revoke_time(self, start_time: datetime) -> bool:
        utcnow = datetime.utcnow()
        if not self.sync:
            return utcnow - self.last_run >= timedelta(seconds=self.interval)
        current_time_in_seconds = int((utcnow - start_time).total_seconds())
        return (
            utcnow > self.last_run
            and (current_time_in_seconds + self.offset) % self.interval == 0
        )

    def update_last_run(self):
        self.last_run = datetime.utcnow()

    def execute(self):
        logger.info(f"Executing: {self.name}")
        event_stream: EventStream = EventStream.get_instance()
        event_stream.publish("execute-job", Event(name=self.name))
        if self.run_thread:
            t = Thread(target=self.func)
            t.daemon = True
            t.start()
        else:
            self.func()
