from components.genericcell import GenericCell

class Cell(GenericCell):
    def __init__(self, type, name, ops=None, in_convs=None, out_convs=None):
        super().__init__()

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


