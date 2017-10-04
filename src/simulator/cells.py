from abc import ABC, abstractmethod
from collections import deque
from generic.graph import GraphNode
from simulator.widgets import RealWidget

#import sys
import pdb

# FIXME make an operation class which creates an operation
# FIXME make most class variables be private

# Consider making GraphNode a parent class of this one rather than doing what I
# am doing
# Move this to generics 
class GenericCell(ABC, GraphNode):
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
    def update(self, delta_time):
        pass

    """
    @abstractmethod
    def enqueue_widget(self):
        pass
    """

class Cell(GenericCell):
    def __init__(self, name, ops=None, network=None):
        super().__init__(name, "cell", ops=ops, network=network)

        # FIXME
        self._queue = deque(maxlen=3)

        # Time
        self.ops["NOP"] = 0
        self.op_start_time = 0
    
    def enqueue(self, widget):
        if len(self._queue) >= self._queue.maxlen:
            return False

        self._queue.append(widget)
        return True

    # TODO
    def update(self, cur_time):
        self._cur_time = cur_time

        # Cell idle
        if self.status is "idle":
            if len(self._queue) > 1:
                widget = self._queue[0]
                self._oper = self.network.process_network_command("controller",
                    "query_operation", widget.id)

                self.status = "operational"
                self._op_start_time = cur_time

        # Cell operational
        if self.status is "operational":
            if self._oper[0] is "NOP":
                self.status = "waiting"

            elif cur_time - self._op_start_time >= self._oper[1]:
                widget =self._queue[0]
                self.network.process_network_command("controller",
                        "notify_completion", widget.id, self._oper[0])
                self.status = "waiting"

        # Cell waiting
        if self.status is "waiting":
            widget = self._queue[0]
            best_next = self.network.process_network_command("controller",
                "query_next", widget.id)

            if best_next.enqueue(widget):
                self.network.process_network_command("controller",
                    "notify_enqueue", widget.id)
                self._queue.popleft()
                self.status = "idle"
            else: 
                self.status = "waiting"

    def log(self):
        widget_str = "Widget: None"
        if len(self._queue) > 0:
            widget_str = (
                "" + str(self.queue[0]) + "\n"
                "Status: " + self.status + "\n"
                "Operation: (" + self._oper[0] + ", " + str(self._oper[1]) + ")\n"
            )

        log_str = (
            "Cell\n----------\n"
            "Name: " + self.name + "\n"
        )

        return log_str

class Conveyor(GenericCell):
    def __init__(self, name="", length=0, network=None):
        super().__init__(name, "conv", label="Conveyor", network=network)

        self.ops["NOP"] = 0

        self.dot_attrs.update({
            "style": "filled, rounded",
            "shape": "box",
            "fillcolor": "deepskyblue",
        })

        self._queue = deque([None] * length, maxlen=length)

    def enqueue(self, widget):
        if not isinstance(self._queue[-1], RealWidget):
            self._queue[-1] = widget
            return True
        else:
            return False

    def update(self, cur_time):
        # Conveyor idle
        if self.status is "idle":
            if isinstance(self._queue[0], RealWidget):
                widget = self._queue[0]
                self._oper = self.network.process_network_command("controller",
                    "query_operation", widget.id)

                self.status = "operational"
                self._op_start_time = cur_time
            else:
                self._queue.append(None)

        # Conveyor operational
        if self.status is "operational":
            if self._oper[0] is "NOP":
                self.status = "waiting"

            elif cur_time - self._op_start_time >= self._oper[1]:
                widget =self._queue[0]
                self.network.process_network_command("controller",
                        "notify_completion", widget.id, self._oper[0])
                self.status = "waiting"

        # Conveyor waiting
        if self.status is "waiting":
            widget = self._queue[0]
            best_next = self.network.process_network_command("controller",
                "query_next", widget.id)

            if best_next.enqueue(widget):
                self.network.process_network_command("controller",
                    "notify_enqueue", widget.id)
                self._queue.popleft()
                self.status = "idle"
            else: 
                self.status = "waiting"
        
    def log(self):
        queue_str = "Queue: [ "
        for widget in self._queue:
            if isinstance(widget, RealWidget):
                queue_str += widget.id + " "
            else:
                queue_str += "None "
        queue_str += "]"

        log_str = (
            "Conveyor\n----------\n"
            "Name: " + self.name + "\n"
            "" + queue_str + "\n"
        )

        return log_str

class Source(GenericCell):
    def __init__(self, name, ops=None, spawn_attrs=None, network=None):
        super().__init__(name, "source", ops=ops, network=network)

        self.dot_attrs.update({
            "style": "filled",
            "fillcolor": "green",
        })

        self._queue = deque(maxlen=1)
            
    def log(self):
        widget_str = "Widget: None"
        if len(self._queue) > 0:
            widget_str = str(self._queue[0])

        log_str = (
            "Source\n----------\n"
            "Name: " + self.name + "\n"
            "" + widget_str + "\n"
        )

        return log_str

    def update(self, cur_time):
        # Source idle
        if self.status == "idle":
            widget_id, self._oper = self.network.process_network_command("controller",
                    "query_instantiate")

            widget = RealWidget(widget_id)
            self._queue.append(widget)

            self.status = "operational"
            self._op_start_time = cur_time

        # Source operational
        elif self.status == "operational":
            if cur_time - self._op_start_time >= self._oper[1]:
                widget = self._queue[0]
                self.network.process_network_command("controller",
                        "notify_completion", widget.id, self._oper[0])
                self.status = "waiting"

        # Source waiting
        if self.status == "waiting":
            widget = self._queue[0]
            best_next = self.network.process_network_command("controller",
                    "query_next", widget.id)

            if best_next.enqueue(widget):
                self.network.process_network_command("controller",
                    "notify_enqueue", widget.id)
                self._queue.popleft()
                self.status = "idle"
            else: 
                self.status = "waiting"

class Sink(GenericCell):
    def __init__(self, name, ops=None, network=None):
        super().__init__(name, "sink", ops=ops, network=network)

        self.dot_attrs.update({
            "style": "filled",
            "fillcolor": "red",
        })

        self.queue = deque(maxlen=1)

    # FIXME
    def update(self, cur_time):
        # Sink idle
        if self.status == "idle":
            if len(self.queue) > 1:
                self._oper = self.network.process_network_command("controller",
                        "query_op", self.queue[0].id)
                        
                self.status = "operational"
                self._op_start_time = cur_time

        # Sink operational
        elif self.status == "operational":
            if cur_time - self._op_start_time >= self._oper[1]:
                self.status = "waiting"

        # Sink waiting
        if self.status == "waiting":
            self.network.process_network_command("controller", "terminate",
                    self.queue[0].id)
            
            self.queue.popleft()

    def log(self):
        widget_str = "Widget: None"
        if len(self.queue) > 0:
            widget_str = str(self.queue[0])

        log_str = (
            "Sink\n----------\n"
            "Name: " + self.name + "\n"
            "" + widget_str + "\n"
        )

        return log_str

