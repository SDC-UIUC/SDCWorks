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

        reqs_dict = {}

        # Add nodes
        req_nodes = []
        for node in nodes:
            req_node = RequirementNode(node[0], op=node[1])
            reqs_dict[req_node.name] = req_node
            if req_node.name == root:
                self.root = req_node
            req_nodes.append(req_node)
        self.add_graph_nodes(req_nodes)

        if not self.root:
            raise ValueError("Root node '%s' not in requirement graph" % (root))

        # Add edges
        if edges:
            for name, nexts in edges:
                req = reqs_dict[name]
                for next in nexts:
                    next = reqs_dict[next]
                    self.add_graph_edges(req, next)

class RequirementNode(GraphNode):
    def __init__(self, name="", label="", op=None):
        super().__init__(name, label)

        self.op = op
