from abc import ABC, abstractmethod

class GenericCell(ABC):
    def __init__(self):
        self.queue = []

    @abstractmethod
    def update(self):
        pass


