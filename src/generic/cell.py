from abc import ABC, abstractmethod
from generic.graph import GenericGraphNode
from generic.widget import GenericWidget
from simulator.operations import Operation

# FIXME have the queue be initialized here (?)
class GenericCell(ABC, GenericGraphNode):
    def __init__(self, name, type, label="", ops=None):
        super().__init__(name, label)    

        # General variables
        self.type = type

        # Plant variables
        noop = Operation("NOP", 0)
        self.ops = { "NOP": noop }
        if ops:
            self.ops.update(ops)
        self._queue = None

        # Controller variables  
        self.action = "NOP"
        self.next_transfer = None
        self.widget_inst = None

    @abstractmethod
    def __str__(self):
        pass

    def _move_widgets(self):
        for widget in self._queue:
            if isinstance(widget, GenericWidget):
                widget.pos -= 1

    def _transfer_widget(self):
        assert len(self._queue) > 0
        assert isinstance(self._queue[0], GenericWidget) == True

        widget = self._queue[0]
        self.next_transfer.enqueue(widget)
        self._queue.popleft()

        if not self.type is "conveyor":
            self._move_widgets()
        else:
            self._queue.appendleft(None)

    def can_enqueue(self):
        if self.type is "conveyor":
            if isinstance(self._queue[-1], type(None)):
                return True
            return False
        else:
            if len(self._queue) < self._queue.maxlen:
                return True
            return False

    @abstractmethod
    def enqueue(self, widget):
        pass

    def head(self):
        if len(self._queue) == 0:
            return None
        return self._queue[0]

    def log(self):
        return str(self)

    def tail(self):
        if len(self._queue) == 0:
            return None
        return self._queue[-1]

    @abstractmethod
    def update(self, cur_time):
        pass
