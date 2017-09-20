from abc import ABC, abstractmethod
from generic.graph import GraphNode
from simulator.widget import Widget

import sys

# Consider making GraphNode a parent class of this one rather than doing what I
# am doing
class GenericCell(ABC):
    @abstractmethod
    def log(self):
        pass

    @abstractmethod
    def update(self, delta_time):
        pass


class Cell(GenericCell, GraphNode):
    def __init__(self, name="", type="", ops=None):
        super().__init__(name)

        self.type = type

        if ops is None:
            ops = {}
        self.ops = ops

        self.nexts = []
        self.prevs = []

        # Storage
        self._real_queue_capacity = 0
        self._real_queue = []
        self._virtual_queue = []

        # Time
        self._cur_time = 0
        self.op_start_time = 0

        # Widget
        self.cur_widget = None

    # Add function to add an output/input conv

    # FIXME
    def get_nexts(self):
        for conv in self.output_convs:
            self.nexts.append(conv.output)

        return self.nexts

    def update(self, delta_time):
        self.cur_time += delta_time

        print("Updates cell")

    def log(self):
        print("Complete me")

    def move_widget(self):
        if not self.widget:
            return

class Conveyor(GenericCell, GraphNode):
    def __init__(self, name="", input=None, output=None, length=0.0):
        super().__init__(name)

        self.length = length
        self.input = input
        self.output = output

    def update(self, delta_time):
        pass

    def log(self):
        pass


class Source(GenericCell, GraphNode):
    def __init__(self, name="", ops=None, spawn_attrs=None):
        super().__init__(name)

        if ops is None:
            ops = {}
        self.ops = ops

        self._cur_time = 0
        self._outputs = []
        self._requirements = None
        self._widget = None

        self.nexts = []
        self.prevs = None

        # Spawn variables
        self._last_spawn_time = -sys.maxsize - 1
        self._spawn_time_type = spawn_attrs["spawn_time_type"]
        if self._spawn_time_type == "constant":
            self._spawn_time = spawn_attrs["spawn_time_interval"]

        self._spawn_req_type = spawn_attrs["spawn_req_type"]
        if self._spawn_req_type == "round-robin":
            self._spawn_req_idx = 0

    def set_requirements(self, requirements):
        self.requirements = requirements

    def log(self):
        log_str = ""

        # FIXME
        if self.widget:
            log_str += "Source %s contains widget with requirement %s" % (self.name, self.widget.req_name)

    def update(self, delta_time):
        self.cur_time += delta_time

        # Check if full
        if not self.widget:
            return

        # Check if should spawn
        spawn = False
        if self._spawn_time_type == "constant":
            if self.cur_time - self.last_spawn_time >= self.spawn_time:
                spawn = True
                self.last_spawn_time = self.cur_time

        # Select requirement to spawn
        if self._spawn_req_type == "round-robin":
            requirement = self.requirements[self.req_idx]
            self.widget = Widget(requirement)
            self.req_idx = (self.req_idx + 1) % len(self.requirements)

    def move_widget(self):
        if not self.widget:
            return
        
class Sink(GenericCell, GraphNode):
    def __init__(self, name="", ops=None):
        super().__init__(name)

        if ops is None:
            ops = {}
        self.ops = ops

        self.cur_time = 0
        self.widget = None

        self.nexts = None
        self.prevs = []


    def update(self, delta_time):
        self.cur_time += delta_time

        if not self.widget is None:
            self.widget = None

    def log(self):
        print("Complete me")

