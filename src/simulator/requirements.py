from collections import OrderedDict
from parser.parser import parse_requirements
from generic.graph import GenericGraph, GenericGraphNode

import pdb

class Requirements(OrderedDict):
    def __init__(self, req_yaml):
        super().__init__(self)

        # Parse requirement YAML
        reqs_data = parse_requirements(req_yaml)
        for req_data in reqs_data:
            requirement = Requirement(**req_data)
            
            if requirement.name in self:
                err_str = (
                    "Key " + requirement.name + " already exists. "
                    "Requirement names must be unique\n"
                )
                raise KeyError(err_str)

            self[requirement.name] = requirement

class Requirement(GenericGraph):
    def __init__(self, name="", nodes=None, root=None, edges=None):
        super().__init__(name)

        # Add nodes
        reqs_dict = {}
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

class RequirementNode(GenericGraphNode):
    def __init__(self, name="", label="", op=None):
        super().__init__(name, label)

        self.op = op
