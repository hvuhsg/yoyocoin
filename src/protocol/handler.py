from abc import ABC, abstractmethod

from loguru import logger


class Handler(ABC):
    @abstractmethod
    def validate(self, message):
        pass

    def log(self, message):
        logger.debug(f"{self.topic}\n-\t{message}")
