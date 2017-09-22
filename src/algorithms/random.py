#from algorithms.utils import generate_all_feasible_paths
from generic.algorithm import Algorithm

import pdb

class Random(Algorithm):
    def __init__(self, plant, requirements):
        self.plant = plant
        self.requirements = requirements

        self.paths = self.generate_all_feasible_paths()

        
    def initialize_routing_tables(self):
        print("Complete me")

    def update_routing_tables(self):
        print("Complete me")
