from abc import ABC


class SingletonNotInitialized(RuntimeError):
    def __init__(self, *args):
        super().__init__(*args)


class Singleton(ABC):
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise SingletonNotInitialized(f"{cls.__name__} is not initialized.")
        return cls._instance

    def __init__(self):
        self.__class__._instance = self
