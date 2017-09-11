from parser.parser import parse_requirements

class Requirements:
    def __init__(self, req_yaml):
        # Parse requirement YAML
        reqs_data = parse_requirements(req_yaml)

        self.requirements = []
        for req_data in reqs_data:
            requirement = Requirement(*req_data)
            self.requirements.append(requirement)

class Requirement:
    def __init__(self, name, nodes, root, edges):
        self.name = name

        nodes_dict = {}
        for node in nodes:
            name = node[0]
            if name in nodes_dict:
                raise KeyError("Duplicate node '%s' with same name" % (node))
            nodes_dict[name] = RequirmentNode(name, node[1])

        if root not in nodes_dict:
            raise ValueError("Root node '%s' not in node list" % (root))
        self.root = nodes_dict[root]

        if edges == None:
            edges = []
            
        for edge in edges:
            name = edge[0]
            if name not in nodes_dict:
                raise ValueError("No key '%s' in requirement '%s'" % (name,
                    self.name))

            nexts = []
            for next in edge[1]:
                if next not in nodes_dict:
                    raise ValueError("No node '%s'" % (next))
                nexts.append(nodes_dict[next])
            nodes_dict[name].nexts = nexts


    def generate_requirment_dot(self, dot_path):
        """Generates a requirement encoded in the DOT language at <dot_path>.
        The generated file can be run throught the 'dot' command to create an
        image file of the conveyance graph.

        Args:
            dot_path (string): path where the encoded conveyance graph will be
                written

        Examples: 
            Requirement.generate_graph_dot(<dot_path>)
            >>> dot <dot_path> -Tpng -o<image_path>

        """
            
        dot_str = []
        visited_nodes = set()
        queue = [self.root]
        
        # BFS through graph
        while len(queue) > 0:
            node = queue.pop(0)
            if node in visited_nodes:
                continue
            visited_nodes.add(node)

            for next in node.nexts:
                if next not in visited_nodes:
                    queue.append(next)

            next_names = [next.name for next in node.nexts]
            next_str = "\t%s -> { %s }\n" % (node.name, " ".join(next_names))
            dot_str.append(next_str)

        dot_str = "strict digraph {\n" + "".join(dot_str) + "}"
        try:
            with open(dot_path, 'w') as dot_file:
                dot_file.write(dot_str)
        except:
            raise EnvironmentError("Unable to open %s" % (dot_path))


class RequirmentNode:
    def __init__(self, name, op, nexts=None):
        self.name = name
        self.op = op
        if nexts == None:
            self.nexts = []
        else:
            self.nexts = nexts

