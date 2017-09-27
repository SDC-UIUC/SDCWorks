

class Network():
    def __init__(self):
        self.dispatch = {
            "controller": {},
            "plant":      {},
        }
        self.controller_dispatch = {}
        self.plant_dispatch = {}

    def process_network_command(self, destination, command, args):
        return self.dispatch[destination][command](args)

    def add_dispatch_command(self, source, command, func):
        self.dispatch[source][command] = func


