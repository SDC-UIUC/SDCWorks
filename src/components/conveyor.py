from components.genericcell import GenericCell

class Conveyor(GenericCell):
    def __init__(self, input, output, length=0.0):
        super().__init__()

        self.length = length
        self.input = input
        self.output = output

    def update(self):
        print("Updates cell")
