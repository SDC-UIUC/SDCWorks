from abc import ABC, abstractmethod
from collections import deque
from generic.graph import GraphNode
from simulator.widget import Widget

import sys

# FIXME make most class variables be private

# Consider making GraphNode a parent class of this one rather than doing what I
# am doing
# Move this to generics 
class GenericCell(ABC, GraphNode):
    def __init__(self, name, type, label=""):
        super().__init__(name, label)    
        
        self.type = type
        self.queue = None
        self.states = ["idle", "operational", "waiting"]

        self.network = None

    @abstractmethod
    def log(self):
        pass

    @abstractmethod
    def update(self, delta_time, control_table):
        pass

    """
    @abstractmethod
    def enqueue_widget(self):
        pass
    """

class Cell(GenericCell):
    def __init__(self, name, ops=None):
        super().__init__(name, "cell")

        if ops is None:
            ops = {}
        self.ops = ops

        # Storage
        self._real_queue_capacity = 0
        self._real_queue = []
        self._virtual_queue = []

        # Time
        self._cur_time = 0
        self.op_start_time = 0

        # Widget
        self.cur_widget = None
    
    # TODO
    def update(self, delta_time, control_table):
        self._cur_time += delta_time
        

    def log(self):
        log_str = (
            "Cell\n----------\n"
            "Name: " + self.name + "\n"
        )

        return log_str

    # FIXME rename to enqueue_widget
    def move_widget(self):
        if not self.widget:
            return

class Conveyor(GenericCell):
    def __init__(self, name="", length=0):
        super().__init__(name, "conv", "Conveyor")

        self.dot_attrs.update({
            "style": "filled, rounded",
            "shape": "box",
            "fillcolor": "deepskyblue",
        })

        self.queue = deque([None] * length, maxlen=length)

    def enqueue_widget(self, widget):
        if not isinstance(self.queue[-1], Widget):
            self.queue[-1] = widget
            return True
        else:
            return False

    def update(self, delta_time, control_table):
        if isinstance(self.queue[0], Widget):
            widget = self.queue[0]
            op, next = widget.get_op_key()
        else:
            self.queue.append(None)
            return

        enqueued = next.enqueue(widget)
        if enqueued:
            self.queue.popleft()
            self.state = "operational"
            self.queue.append(None)
        else:
            self.state = "idle"

    def log(self):
        queue_str = "Queue: [ "
        for widget in self.queue:
            if isinstance(widget, Widget):
                queue_str += widget.id + " "
            else:
                queue_str += "None "

        log_str = (
            "Conveyor\n----------\n"
            "Name: " + self.name + "\n"
            "" + queue_str + "\n"
        )

        return log_str


class Source(GenericCell):
    def __init__(self, name, ops=None, spawn_attrs=None):
        super().__init__(name, "source")

        self.dot_attrs.update({
            "style": "filled",
            "fillcolor": "green",
        })

        if ops is None:
            ops = {}
        self.ops = ops

        self._cur_time = 0
        self._outputs = []
        self._requirements = None
        
        # Widget variables
        maxlen = 1 # FIXME
        self.queue = deque(maxlen=maxlen)

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

    """
    def get_nexts(self, cells=False):
        if not cells:
            return self.conv_nexts
        else:
            return self.nexts
    """

    def log(self):
        widget_str = "Widget: None"
        if len(self.queue) > 0:
            widget_str = str(self.queue[0])

        log_str = (
            "Source\n----------\n"
            "Name: " + self.name + "\n"
            "" + widget_str + "\n"
        )

        return log_str

    # FIXME need to check for states
    def update(self, delta_time, control_table):
        self._cur_time += delta_time

        widget = self._spawn_widget()
        if not widget:
            return
        self.queue.append(widget)
        
        # Get control actions
        widget = self.queue[0]
        op, next = self._widget.get_op_key()

        # FIXME works for a source with one widget but this has to be fixed for
        # multiple widgets because the work time won't be self._last_spawn_time
        op_time = self.ops[op]
        if self._cur_time - self._last_spawn_time >= op_time:
            enqueued = next.enqueue_widget(widget)
            if enqueued:
                self.queue.popleft()

    # FIXME this can be renamed to enqueue_widget()
    def _spawn_widget(self):
        # Check if spawn widget
        if len(self.queue) == self.queue.maxlen:
            return None

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

        return Widget(requirement)

    """
    def enqueue_widget(self):
        if not self.widget:
            return
    """
        
class Sink(GenericCell):
    def __init__(self, name, ops=None):
        super().__init__(name, "sink")

        self.dot_attrs.update({
            "style": "filled",
            "fillcolor": "red",
        })

        if ops is None:
            ops = {}
        self.ops = ops

        self.cur_time = 0

        # Widget variables
        self._widget = None
        self._del_widget = None
        
    def update(self, delta_time, control_table):
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

