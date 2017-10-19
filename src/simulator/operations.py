class Operations(dict):
    def __init__(self, op_list):
        for op in op_list:
            op = Operation(*op)
            self[op.name] = op

class Operation:
    def __init__(self, name, duration):
        self.name = name
        self.duration = duration

    def __str__(self):
        s = "Operation: (%s, %d)" % (self.name, self.duration)
        return s
