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

        for node in nodes:
            if not isinstance(node, GraphNode):
                err_str = "Node %s is not of type GraphNode" % (node)
                raise TypeError(err_str)

        # Add nodes to graph
        for node in nodes:
            if node in self.node_dict:
                raise ValueError("graph_node '%s' is already in graph '%s'" %
                    (node, self.node_dict))

            self.node_dict[node.id] = node
            self._add_dot_node(node)

    def _add_dot_edge(self, node, edge):
        self.graph_dot.add_edge(pydot.Edge(node, edge))
   
    def add_graph_edges(self, node, edges):
        # Check next type
        if isinstance(edges, GraphNode):
            edges = [edges]

        for edge in edges:
            if not isinstance(edge, GraphNode):
                err_str = "Edge %s is not of type GraphNode" % (edge)
                raise TypeError(err_str)

        # Check if node/edges added to graph
        if not node.id in self.node_dict:
            err_str = "Node %s has not been added to graph" % (node)
            raise KeyError(err_str)

        for edge in edges:
            if not edge.id in self.node_dict:
                err_str = "Edge %s has not been added to graph" % (edge)
                raise KeyError(err_str)


        for edge in edges:
            node.add_nexts(edge)
            edge.add_prevs(node)
            self._add_dot_edge(node.id, edge.id)
                    
    def generate_output_files(self, dot_path, png_path):
        self.graph_dot.write_raw(dot_path)
        self.graph_dot.write_png(png_path)

# FIXME make _nexts/_prevs readonly but can change it with add_prev/next
class GraphNode:
    def __init__(self, name="", label=""):
        self.name = name
        self.id = str(uuid4())
        self.label = name
        if  label:
            self.label = label

        self.dot_attrs =  { 
            "name": self.id,
            "label": self.label,
        }
        self._nexts = []
        self._prevs = []

    def __repr__(self):
        repr = "<%s, %r>" % (self.__class__, self.__dict__)
        return repr

    def add_nexts(self, nexts):
        if isinstance(nexts, GraphNode):
            nexts = [nexts]
        self._nexts.extend(nexts)

    def add_prevs(self, prevs):
        if isinstance(prevs, GraphNode):
            prevs = [prevs]
        self._prevs.extend(prevs)

    def get_nexts(self):
        return self._nexts

    def get_prevs(self):
        return self._prevs

