from uuid import uuid4
import pydot

import pdb

class Graph:
    def __init__(self, name, root=None):
        self.root = root
        self.name = name
        self.node_dict = {}

        self.graph_dot = pydot.Dot(graph_name=name, graph_type="digraph")

    def __repr__(self):
        repr = "<%s, %r>" % (self.__class__, self.__dict__)
        return repr

    def _add_dot_node(self, node):
        self.graph_dot.add_node(pydot.Node(**node.dot_attrs))

    def add_graph_nodes(self, nodes):
        # Check nodes type
        if isinstance(nodes, GraphNode):
            nodes = [nodes]

        if not all(isinstance(node, GraphNode) for node in nodes):
            err_str = "'%s' is not of type 'GraphNode" % (node)
            raise TypeError(err_str)

        # Add nodes to graph
        for node in nodes:
            if node in self.node_dict:
                raise ValueError("graph_node '%s' is already in graph '%s'" %
                    (node, self.node_dict))

            self.node_dict[node.name]=  node
            self._add_dot_node(node)

    def _add_dot_edge(self, node, edge):
        self.graph_dot.add_edge(pydot.Edge(node, edge))
   
    def add_graph_edges(self, node, edges):
        # Check next type
        if isinstance(edges, str):
            edges = [edges]

        if not all(isinstance(edge, str) for edge in edges):
            err_str = "'%s' is not of type 'String'" % (edge)
            raise TypeError(err_str)

        for edge in edges:
            self.node_dict[node].nexts.append(self.node_dict[edge])
            self._add_dot_edge(node, edge)
                    
    def generate_output_files(self, dot_path, png_path):
        self.graph_dot.write_raw(dot_path)
        self.graph_dot.write_png(png_path)

class GraphNode:
    def __init__(self, name="", nexts=None):
        self.name = name
        self.dot_attrs =  { "name": name }

        if nexts == None:
            self.nexts = []
        else:
            self.nexts = nexts

    def __repr__(self):
        repr = "<%s, %r>" % (self.__class__, self.__dict__)
        return repr

    def get_nexts(self):
        return self.nexts

