
class Event:
    def __init__(self, name, **kwargs):
        self.name = name
        self.args = kwargs

    def __str__(self):
        return f"Event(name='{self.name}', args={self.args})"
