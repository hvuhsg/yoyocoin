from threading import Thread
from functools import wraps
from datetime import datetime, timedelta, tzinfo
from time import sleep


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
        return utcnow > self.last_run and (current_time_in_seconds + self.offset) % self.interval == 0

    def update_last_run(self):
        self.last_run = datetime.utcnow()

    def execute(self):
        if self.sync:
            print(f"{datetime.now()} Execute {self.name}")
        if self.run_thread:
            t = Thread(target=self.func)
            t.daemon = True
            t.start()
        else:
            self.func()


class Scheduler(Thread):
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise ValueError("Scheduler must be initialized first")
        return cls._instance

    @classmethod
    def schedule(cls, name: str, interval: float, sync: bool = True, run_thread: bool = True, offset: int = 0):
        scheduler = cls.get_instance()

        def decorator(func):
            @wraps(func)
            def wrapped(*args, **kwargs):
                return func(*args, **kwargs)
            scheduler.add_job(wrapped, name, interval, sync, run_thread)
            return wrapped
        return decorator

    def __init__(self, time_start: datetime = None, min_time_step: float = 1.0):
        super().__init__()
        if time_start is None:
            time_start = datetime.fromtimestamp(0)  # TODO: set to utc time zone
        self.time_start = time_start
        self.min_time_step = min_time_step  # check jobs every <min_time_step> seconds
        self._stop = False

        self.jobs = {}  # name: job

        self.__class__._instance = self

    def add_job(self, func, name, interval, sync, run_thread, offset: int = 0):
        self.jobs[name] = Job(func=func, name=name, interval=interval, sync=sync, run_thread=run_thread, offset=offset)

    def remove_job(self, name):
        return self.jobs.pop(name, None)

    def job_list(self):
        return list(self.jobs.values())

    def check_jobs(self):
        for job_name, job in self.jobs.items():
            if job.is_revoke_time(start_time=self.time_start):
                job.execute()
                job.update_last_run()

    def run(self) -> None:
        while not self._stop:
            self.check_jobs()
            sleep(self.min_time_step)

    def stop(self):
        self._stop = True
