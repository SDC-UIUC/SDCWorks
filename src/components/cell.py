from generic.graph import GraphNode

class Cell(GraphNode):
    def __init__(self, name="", nexts=None, type="", ops=None):
        GraphNode.__init__(name, nexts)
        GenericCell

        self.type = type
        self.name = name

        if ops == None:
            self.ops = {}
        else:
            self.ops = ops

        self.input_convs = []
        self.output_convs = []

    def get_nexts(self):
        nexts = []
        for conv in self.output_convs:
            nexts.append(conv.output)

        return nexts

    def update(self):
        print("Updates cell")


