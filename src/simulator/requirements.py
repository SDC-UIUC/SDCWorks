from parser.parser import parse_requirements
from generic.graph import Graph, GraphNode

import pdb

class Requirements(list):
    def __init__(self, req_yaml):
        list.__init__(self)

        # Parse requirement YAML
        reqs_data = parse_requirements(req_yaml)

        for req_data in reqs_data:
            requirement = Requirement(**req_data)
            self.append(requirement)

class Requirement(Graph):
    def __init__(self, name="", nodes=None, root=None, edges=None):
        super().__init__(name)

        self.root = root
        
        # Add nodes
        req_nodes = list(map(lambda n: RequirementNode(n[0], ops=n[1]), nodes))
        self.add_graph_nodes(req_nodes)

        if root not in self.node_dict:
            raise ValueError("Root node '%s' not in requirement graph" % (root))

        # Add edges
        if edges:
            for edge in edges:
                self.add_graph_edges(edge[0], edge[1])

class RequirementNode(GraphNode):
    def __init__(self, name="", nexts=None, label="", ops=None):
        super().__init__(name, nexts)

        if label:
            self.attrs["label"] = label
        self.ops = ops
