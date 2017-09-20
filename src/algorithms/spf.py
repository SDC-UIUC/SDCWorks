from generic.graph import Graph
from copy import copy

import pdb

class SPF:
    def __init__(self, requirements):
        self.requirements = requirements

        print("Complete me")

# I probably don't need this
class ConveyanceGraph(Graph):
    def __init__(self, root):
        

        self.root = root
    
class ConveyanceNode():
    def __init__(self, ref, nexts=None):
        self.ref = ref
        self.id = uuid4()
        self.name = ref.name
        self.background_color = "white"
        if nexts == None:
            self.nexts = []
        else:
            self.nexts = nexts
