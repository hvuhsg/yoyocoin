import time


class MultiSubscribersQueue:
    def __init__(self):
        self.events = []

    def get(self, offset):
        while offset >= len(self.events):
            time.sleep(0.1)
        return self.events[offset]

    def put(self, event):
        self.events.append(event)
