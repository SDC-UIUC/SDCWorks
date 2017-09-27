from uuid import uuid4
import pydot

import pdb

# FIXME naming of things in the future
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

            self.node_dict[node.id]=  node
            self._add_dot_node(node)

    def _add_dot_edge(self, node, edge):
        self.graph_dot.add_edge(pydot.Edge(node, edge))
   
    def add_graph_edges(self, node, edges):
        # Check next type
        if isinstance(edges, GraphNode):
            edges = [edges]

        if not all(isinstance(edge, GraphNode) for edge in edges):
            err_str = "'%s' is not of type 'String'" % (edge)
            raise TypeError(err_str)

        for edge in edges:
            node.add_nexts(edge)
            edge.add_prevs(node)
            self._add_dot_edge(node.id, edge.id)
                    
    def generate_output_files(self, dot_path, png_path):
        self.graph_dot.write_raw(dot_path)
        self.graph_dot.write_png(png_path)

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
        self._nexts = None
        self._prevs = None

    def __repr__(self):
        repr = "<%s, %r>" % (self.__class__, self.__dict__)
        return repr

    def add_nexts(self, nexts):
        if not self._nexts:
            self._nexts = []

        if isinstance(nexts, GraphNode):
            nexts = [nexts]
        self._nexts.extend(nexts)

    def add_prevs(self, prevs):
        if not self._prevs:
            self._prevs = []

        if isinstance(prevs, GraphNode):
            prevs = [prevs]
        self._prevs.extend(prevs)

    # FIXME maybe (?)
    def get_nexts(self):
        if not self._nexts:
            return []
        return self._nexts

    def get_prevs(self):
        if not self._prevs:
            return []
        return self._prevs

