from abc import ABC, abstractmethod
from generic.graph import GraphNode
from simulator.widget import Widget

import sys

# Consider making GraphNode a parent class of this one rather than doing what I
# am doing
# Move this to generics
class GenericCell(ABC):
    @abstractmethod
    def log(self):
        pass

    @abstractmethod
    def update(self, delta_time):
        pass


class Cell(GenericCell, GraphNode):
    def __init__(self, name="", ops=None):
        super().__init__(name)

        self.type = "cell"

        if ops is None:
            ops = {}
        self.ops = ops

        self.nexts = []
        self.conv_nexts = []
        self.prevs = []
        self.conv_prevs = []

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
    def get_nexts(self, cells=False):
        if not cells:
            return self.conv_nexts
        else:
            return self.nexts

    # TODO
    def update(self, delta_time):
        self._cur_time += delta_time
        

    def log(self):
        log_str = (
            "Cell\n----------\n"
            "Name: " + self.name + "\n"
        )

        return log_str

    def move_widget(self):
        if not self.widget:
            return

class Conveyor(GenericCell, GraphNode):
    def __init__(self, name="", length=0.0, prev=None, next=None):
        super().__init__(name)

        self.length = length
        self.prevs = [prev]
        self.nexts = [next]

    def update(self, delta_time):
        pass

    def log(self):
        log_str = (
            "Conveyor\n----------\n"
            "Name: " + self.name + "\n"
        )

        return log_str


class Source(GenericCell, GraphNode):
    def __init__(self, name="", ops=None, spawn_attrs=None):
        super().__init__(name)

        self.type = "source"

        if ops is None:
            ops = {}
        self.ops = ops

        self._cur_time = 0
        self._outputs = []
        self._requirements = None

        self.nexts = []
        self.conv_nexts = []
        self.prevs = None
        self.prev_nexts = None

        # Widget variables
        self._widget = None

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

    def get_nexts(self, cells=False):
        if not cells:
            return self.conv_nexts
        else:
            return self.nexts

    def log(self):
        widget_str = "Widget: None"
        if self._widget:
            widget_str = str(self._widget)

        log_str = (
            "Source\n----------\n"
            "Name: " + self.name + "\n"
            "" + widget_str + "\n"
        )

        return log_str

    def update(self, delta_time):
        self._cur_time += delta_time

        # Check if widget present
        if self._widget:
            return

        # Check if spawn widget
        spawn = False
        if self._spawn_time_type == "constant":
            if self._cur_time - self._last_spawn_time >= self._spawn_time:
                spawn = True
                self._last_spawn_time = self._cur_time

        # Select requirement to spawn
        if self._spawn_req_type == "round-robin":
            requirement = self.requirements[self._spawn_req_idx]
            self._widget = Widget(requirement)
            self._spawn_req_idx = (self._spawn_req_idx + 1) % len(self.requirements)

    def move_widget(self):
        if not self.widget:
            return
        
class Sink(GenericCell, GraphNode):
    def __init__(self, name="", ops=None):
        super().__init__(name)

        self.type = "sink"

        if ops is None:
            ops = {}
        self.ops = ops

        self.cur_time = 0

        # Widget variables
        self._widget = None
        self._del_widget = None

        self.nexts = None
        self.conv_nexts = None
        self.prevs = []
        self.conv_prevs = []


    def update(self, delta_time):
        self.cur_time += delta_time

        # Terminate widget
        self._del_widget = None
        if not self._widget is None:
            self._del_widget = self._widget
            self._widget = None

    def log(self):
        widget_str = "Widget: None"
        if self._del_widget:
            widget_str = str(self._widget)

        log_str = (
            "Sink\n----------\n"
            "Name: " + self.name + "\n"
            "" + widget_str + "\n"
        )

        return log_str

