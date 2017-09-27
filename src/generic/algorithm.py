from abc import ABC, abstractmethod
from copy import copy
from generic.graph import Graph, GraphNode

import pdb

class Algorithm(ABC):
    def __init__(self, plant, requirements):
        self.plant = plant
        self.requirements = requirements

        #self.reqs_paths = self.generate_all_feasible_paths()

    @abstractmethod
    def initialize_routing_tables(self):
        pass

    @abstractmethod
    def update_routing_tables(self):
        pass

    def generate_all_feasible_paths(self):
        reqs_paths = []
        for requirement in self.requirements:
            req_paths = []
            cg = RequirementPath(requirement.name, req_paths)
            visited_cells = {}
            sources = self.plant.cells["source"]
            for source in sources:
                paths = self.generate_feasible_paths(requirement.root, source, 
                                                     visited_cells, 0, cg)
                req_paths.extend(paths)
            reqs_paths.append(cg) 

        return reqs_paths

                
    def generate_feasible_paths(self, req, cell, visited, num_ops, cg):
        # Check if cell visited
        if cell in visited:
            if visited[cell] == num_ops:
                return [None]
        visited[cell] = num_ops

        # Check if end reached
        if cell.type == "sink":
            if req.op == "TERMINATE":
                cg_node = RequirementPathNode(cell, None, req.op)
                cg.add_graph_nodes(cg_node)
                return [cg_node]
            else:
                return [None]

        # Check if requirement operation satisfied
        req_nexts = [req]
        req_sat = False
        if not cell.type is "conv" and req.op in cell.ops:
            req_nexts.extend(req.get_nexts())
            req_sat = True

        # Iterate over all next requirements requirements
        paths = []
        for req_next in req_nexts:
            visited_param = copy(visited)
            num_ops_param = num_ops
            skip_req = True
            if not req_next is req:  
                visited_param[cell] += 1
                num_ops_param += 1
                skip_req = False

            for next in cell.get_nexts():
                feasible_paths = \
                    self.generate_feasible_paths(req_next, next, 
                                                 visited_param,
                                                 num_ops_param, cg)

                # Prepend current node to returned paths
                for feasible_path in feasible_paths:
                    if not feasible_path:
                        continue

                    if skip_req:
                        cg_node = RequirementPathNode(cell, next, "PASS", skip_req)
                    else:
                        cg_node = RequirementPathNode(cell, next, req.op, skip_req)
                    cg.add_graph_nodes(cg_node)
                    cg.add_graph_edges(cg_node, feasible_path)
                    paths.append(cg_node)

        return paths

class RequirementPath(Graph):
    def __init__(self, name, root):
        super().__init__(name, root)

class RequirementPathNode(GraphNode):
    def __init__(self, ref, next, op):
        super().__init__(ref.name)

        self.ref = ref
        self.id = ref.id
        self.next = next
        self.op = op
        self.weight = 0

        if not op is "PASS":
            self.dot_attrs["fillcolor"] = "white"
        else:
            self.dot_attrs["fillcolor"] = "ivory4"
