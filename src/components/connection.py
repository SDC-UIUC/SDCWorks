class Connection:
    def __init__(self, length=0.0, endpoints=None):
        self.length = length
        if endpoints == None:
            self.endpoints = set()
        else:
            self.endpoints = endpoints
