from collections import Counter
from generic.algorithm import Algorithm
from random import randrange

import pdb

class First(Algorithm):
    def __init__(self, plant, requirements):
        super().__init__(plant, requirements)
        
    def initialize_routing_tables(self):
        # Select the first calculated path for a requirement
        for req_paths in self.reqs_paths:
            req_paths.root = req_paths.root[0]
            
            # Iterate through the path
            visit_counter = Counter()
            node = req_paths.root
            while True:
                visit_counter[node.id] = +1

                key = (req_paths.name, visit_counter[node.id])
                value = (node.op, node.next)
                self.plant.update_control_table(node.id, key, value)

                nexts = node.get_nexts()
                if not nexts:
                    break
                node = nexts[0]


    def update_routing_tables(self):
        print("Complete me")
