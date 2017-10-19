from collections import deque
from custom.cell import CustomCell
from custom.widget import CustomWidget
from generic.widget import GenericWidget
from simulator.operations import Operation

import pdb

class Cell(CustomCell):
    def __init__(self, name, length=1, ops=None):
        super().__init__(name, "cell", ops=ops)
        self._queue = deque(maxlen=length)

    def __str__(self):
        action_str = "Action: " + str(self.action)

        queue_str = "Queue: [ "
        for i in range(self._queue.maxlen):
            if i < len(self._queue):
                queue_str += self._queue[i].id + " "
            else:
                queue_str += "None "
        queue_str += "]"

        cell_str = (
            "Cell\n----------\n"
            "Name: " + self.name + "\n"
            "" + action_str + "\n"
            "" + queue_str + "\n"
        )
        return cell_str
    
    def enqueue(self, widget):
        assert len(self._queue) < self._queue.maxlen
        self._queue.append(widget)

        widget.loc = self
        widget.pos = len(self._queue)

    def update(self, cur_time):
        # Determine which action to perform
        if self.action == "transfer":
            self._transfer_widget()
        elif self.action in self.ops:
            pass
        else:
            raise ValueError("Cell received invalid action: %s" % (self.action))
    
class Conveyor(CustomCell):
    def __init__(self, name="", length=1):
        super().__init__(name, "conveyor", label="Conveyor")

        self.dot_attrs.update({
            "style": "filled, rounded",
            "shape": "box",
            "fillcolor": "deepskyblue",
        })

        self._queue = deque([None] * length, maxlen=length)

    def __str__(self):
        action_str = (
            "Action: " + str(self.action) + ""
            ", wait: " + str(self.wait_time) + ""
        )

        queue_str = "Queue: [ "
        for widget in self._queue:
            if isinstance(widget, GenericWidget):
                queue_str += widget.id + " "
            else:
                queue_str += "None "
        queue_str += "]"

        assert len(self._prevs) == 1
        assert len(self._nexts) == 1

        conv_str = (
            "Conveyor\n----------\n"
            "Prev: " + self._prevs[0].name + " next: " + self._nexts[0].name + "\n"
            "" + action_str + "\n"
            "" + queue_str + "\n"
        )
        return conv_str
    
    def enqueue(self, widget):
        assert isinstance(self._queue[-1], type(None))
        self._queue[-1] = widget

        widget.loc = self
        widget.pos = len(self._queue)
    
    def update(self, cur_time):
        # Determine which action to perform
        if self.action == "move":
            assert isinstance(self._queue[0], type(None))
            self._queue.append(None)
            self._move_widgets()
        elif self.action == "transfer":
            self._transfer_widget()
        elif self.action in self.ops:
            pass
        else:
            raise ValueError("Conveyor received invalid action: %s" % (self.action))

class Source(CustomCell):
    def __init__(self, name, length=1):
        super().__init__(name, "source")

        self.dot_attrs.update({
            "style": "filled",
            "fillcolor": "green",
        })

        self._queue = deque(maxlen=length)
        inst = Operation("INSTANTIATE", 0)
        self.ops[inst.name] = inst

    def __str__(self):
        action_str = "Action: " + str(self.action)

        queue_str = "Queue: [ "
        for i in range(self._queue.maxlen):
            if i < len(self._queue):
                queue_str += self._queue[i].id + " "
            else:
                queue_str += "None "
        queue_str += "]"

        source_str = (
            "Source\n----------\n"
            "" + action_str + "\n"
            "" + queue_str + "\n"
       ) 
        return source_str 
    
    def enqueue(self, widget):
        assert self.can_enqueue() == True
        self._queue.append(widget)

        widget.loc = self
        widget.pos = len(self._queue)

    def update(self, cur_time):
        # Determine which action to perform
        if self.action == "instantiate":
            widget = self.widget_inst
            self.enqueue(widget) 
        elif self.action == "transfer":
            self._transfer_widget() 
        elif self.action in self.ops:
            pass
        else:
            raise ValueError("Source received invalid action: %s" % (self.action))

class Sink(CustomCell):
    def __init__(self, name, length=1):
        super().__init__(name, "sink")

        self.dot_attrs.update({
            "style": "filled",
            "fillcolor": "red",
        })

        self._queue = deque(maxlen=length)
        term = Operation("TERMINATE", 0)
        self.ops[term.name] = term

    def __str__(self):
        action_str = "Action: " + str(self.action)

        queue_str = "Queue: [ "
        for i in range(self._queue.maxlen):
            if i < len(self._queue):
                queue_str += self._queue[i].id + " "
            else:
                queue_str += "None "
        queue_str += "]"

        sink_str = (
            "Sink\n---------\n"
            "" + action_str + "\n"
            "" + queue_str + "\n"
        )
        return sink_str
    
    def enqueue(self, widget):
        assert self.can_enqueue() == True
        self._queue.append(widget)

        widget.loc = self
        widget.pos = len(self._queue)

    def update(self, cur_time):
        # Determine which action to perform
        if self.action == "terminate":
            widget = self._queue.popleft()
            widget.loc = None
            widgetpos = -1
            self._move_widgets()
        elif self.action in self.ops:
            pass
        else:
            raise ValueError("Sink" % (self.action))

