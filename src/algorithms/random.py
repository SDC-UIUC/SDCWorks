from collections import Counter
from generic.algorithm import Algorithm
from random import randrange

import pdb

class Random(Algorithm):
    def __init__(self, plant, requirements):
        self.plant = plant
        self.requirements = requirements

        self.reqs_paths = self.generate_all_feasible_paths()
        
    def initialize_routing_tables(self):
        # Select a random path for each requirement
        # FIXME fix the naming of variables here
        for req_paths in self.reqs_paths:
            num_paths = len(req_paths.root)
            random_idx = randrange(num_paths)
            random_path = req_paths.root[random_idx]
            req_paths.root = random_path
            
            pdb.set_trace()

            # Iterate through the path
            visit_counter = Counter()
            node = req_paths.root
            while node:
                visit_counter[node.name] = +1

                key = (req_paths.name, visit_counter[node.name])
                value = (node.op, node.conv) # FIXME
                self.plant.update_control_table(node.name, key, value)

                # FIXME
                node = node.nexts[0]


    def update_routing_tables(self):
        print("Complete me")
