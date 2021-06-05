"""
This class is responsible for managing data on disk
the class is exposing key value storage api

read(key)
write(key, value)
"""


class Storage:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise ValueError("Storage must be initialize first.")
        return cls._instance

    def __init__(self, filename: str):
        self.filename = filename
        self._instance = self

    def read(self, key):
        return NotImplemented

    def write(self, key, value):
        return NotImplemented
