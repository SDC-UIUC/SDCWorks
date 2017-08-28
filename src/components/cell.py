# TODO define the repr and str methods to simplify life

class Cell:
    def __init__(self, type, name, ops=None, conns=None):
        self.type = type
        self.name = name
        if ops == None:
            self.ops = []
        else:
            self.ops = ops
        if conns == None:
            self.conns = []
        else:
            self.conns = conns

    def get_nexts(self):
        nexts = []
        for conn in self.conns:
            for endpoint in conn.endpoints:
                if endpoint != self:
                    nexts.append(endpoint)

        return nexts


