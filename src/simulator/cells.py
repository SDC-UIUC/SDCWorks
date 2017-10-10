from collections import deque
from generic.cell import GenericCell
from generic.widget import GenericWidget
from simulator.operations import Operation

import pdb

# FIXME make most class variables be private


class Cell(GenericCell):
    def __init__(self, name, ops=None, network=None):
        super().__init__(name, "cell", ops=ops, network=network)

        # FIXME
        self._queue = deque(maxlen=3)

        # Time
        noop = Operation("NOP", 0)
        self.ops[noop.name] = noop
        self.op_start_time = 0
    
    def enqueue(self, widget):
        if len(self._queue) >= self._queue.maxlen:
            return False

        self._queue.append(widget)
        return True

    def update(self, cur_time):
        # Cell idle
        if self.status is "idle":
            if len(self._queue) > 0:
                widget = self._queue[0]
                self._op = self.network.process_network_command("controller",
                    "query_operation", widget.id)

                self.status = "operational"
                self._op_start_time = cur_time

        # Cell operational
        if self.status is "operational":
            if cur_time - self._op_start_time >= self._op.duration:
                widget =self._queue[0]
                self.network.process_network_command("controller",
                        "notify_completion", widget.id, self._op.name, cur_time)
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
        if self.status == "idle":
            oper_str = "Operation: (None)"
        else:
            oper_str = str(self._op)

        queue_str = "Queue: [ "
        for i in range(self._queue.maxlen):
            if i < len(self._queue):
                queue_str += self._queue[i].id + " "
            else:
                queue_str += "None "
        queue_str += "]"

        log_str = (
            "Cell\n----------\n"
            "Name: " + self.name + "\n"
            "Status: " + self.status + "\n"
            "" + oper_str + "\n"
            "" + queue_str + "\n"
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
        if not isinstance(self._queue[-1], GenericWidget):
            self._queue[-1] = widget
            return True
        else:
            return False

    def transfer(self):
        assert(len(self._nexts) > 0)
        next = self._nexts[0]
        widget = self._queue[0]

        if next.enqueue(widget):
            self.network.process_network_command("controller", 
                "notify_enqueue", widget.id)
            self._queue[0] = None

    # FIXME need to see whether should move or not
    def update(self, cur_time):
        if not self._queue[0]:
            self.wait_time = 0
            self._queue.append(None)
            self.status = "operational"
        else:
            self.wait_time += 1
            self.status = "waiting"
                        
    def log(self):
        queue_str = "Queue: [ "
        for widget in self._queue:
            if isinstance(widget, GenericWidget):
                queue_str += widget.id + " "
            else:
                queue_str += "None "
        queue_str += "]"

        log_str = (
            "Conveyor\n----------\n"
            "Prev: " + self._prevs[0].name + " next: " + self._nexts[0].name + "\n"
            "" + queue_str + "\n"
        )

        return log_str

class Source(GenericCell):
    def __init__(self, name, spawn_attrs=None, network=None):
        super().__init__(name, "source", network=network)

        self.dot_attrs.update({
            "style": "filled",
            "fillcolor": "green",
        })

        self._queue = deque(maxlen=1)
        inst = Operation("INSTANTIATE", 0)
        self.ops[inst.name] = inst
            
    def log(self):
        widget_str = "Widget: None"
        if len(self._queue) > 0:
            widget_str = "Widget: " + self._queue[0].id

        log_str = (
            "Source\n----------\n"
            "Name: " + self.name + "\n"
            "" + widget_str + "\n"
        )

        return log_str

    def update(self, cur_time):
        # Source idle
        if self.status == "idle":
            widget, self._op = self.network.process_network_command("controller",
                                                                    "query_instantiate", 
                                                                    cur_time)
            
            self._queue.append(widget)
            self.network.process_network_command("controller",
                                                 "notify_completion", 
                                                 widget.id, 
                                                 self._op.name, 
                                                 cur_time)

            self.status = "waiting"
        
        # Source waiting
        elif self.status == "waiting":
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
    def __init__(self, name, network=None):
        super().__init__(name, "sink", network=network)

        self.dot_attrs.update({
            "style": "filled",
            "fillcolor": "red",
        })

        self._queue = deque(maxlen=1)
        term = Operation("TERMINATE", 0)
        self.ops[term.name] = term

    def enqueue(self, widget):
        if len(self._queue) >= self._queue.maxlen:
            return False

        self._queue.append(widget)
        return True

    def update(self, cur_time):
        # Sink idle
        if len(self._queue) > 0:
            widget = self._queue[0]
            self._op = self.network.process_network_command("controller",
                "query_operation", widget.id)

            self.network.process_network_command("controller",
                    "notify_completion", self._queue[0].id, self._op.name,
                    cur_time)
            self._queue.popleft()

    def log(self):
        widget_str = "Widget: None"
        if len(self._queue) > 0:
            widget_str = "Widget: " + self._queue[0].id

        log_str = (
            "Sink\n----------\n"
            "Name: " + self.name + "\n"
            "" + widget_str + "\n"
        )

        return log_str

