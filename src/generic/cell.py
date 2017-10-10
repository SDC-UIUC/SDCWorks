from abc import ABC, abstractmethod
from generic.graph import GenericGraphNode

class GenericCell(ABC, GenericGraphNode):
    def __init__(self, name, type, label="", ops=None, network=None):
        super().__init__(name, label)    

        self.type = type
        self.network = network
        self.ops = {}
        if ops:
            self.ops = ops

        self._queue = None
        self.status = "idle"

    @abstractmethod
    def log(self):
        pass

    @abstractmethod
    def update(self, cur_time):
        pass
