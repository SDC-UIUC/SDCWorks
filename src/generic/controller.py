from abc import ABC, abstractmethod

class GenericController(ABC):
    def __init__(self, network, requirement):
        self.network = network
        self.requirements = requirements

    @abstractmethod
    def update(self, cur_time):
        pass
