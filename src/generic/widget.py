from abc import ABC
from uuid import uuid4

class GenericWidget(ABC):
    def __init__(self, req_name):
        # General variables
        self.id = str(uuid4())
        self.req_name = req_name

        # Plant variables
        self.position = 0
        self.location = None
