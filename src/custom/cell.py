from generic.cell import GenericCell

class CustomCell(GenericCell):
    def __init__(self, name, type, label="", ops=None):
        super().__init__(name, type, label=label, ops=ops)

        # Additional controller variables
        self.cost = 0
        self.next_transfer = {}
        self.op_start_time = 0
        self.status = "idle"
        self.wait_time = 0

    def set_cost(self):
        cost = 0
        for widget in self._queue:
            if not isinstance(widget, type(None)):
                cost += 1
        self.cost = cost
