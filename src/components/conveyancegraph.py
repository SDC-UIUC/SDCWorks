from parser.parser import parse_graph
from copy import copy
from uuid import uuid4

import pdb

class ConveyanceGraph:
    def __init__(self, graph_yaml):
        """Builds a conveyance graph from the description provided in the input
        file

        Args:
            graph_yaml (string): path to the YAML file with the graph
                description           

        """

        self.sources = []
        self.sinks = []

        # Parse graph YAML
        cells, convs = parse_graph(graph_yaml)

        # Create dictionary of cells
        cells_dict = {}
        for cell in cells:
            if cell.name in cells_dict:
                # FIXME print out both the cells
                raise ValueError("Duplicate name %s" % (name))

            cells_dict[cell.name] = cell
            if cell.type == "source":
                cell.ops["INSTANTIATE"] = 0
                self.sources.append(cell)
            if cell.type == "sink":
                cell.ops["TERMINATE"] = 0
                self.sinks.append(cell)

        # Create graph
        for conv in convs:
            if conv.input not in cells_dict:
                raise ValueError("No cell with name %s" % (conv.input))
            cell = cells_dict[conv.input]
            cell.output_convs.append(conv)
            conv.input = cell

            if conv.output not in cells_dict:
                raise ValueError("No cell with name %s" % (conv.output))
            cell = cells_dict[conv.output]
            cell.input_convs.append(conv)
            conv.output = cell

        
    def generate_graph_dot(self, dot_path):
        """Generates a conveyance graph encoded in the DOT langueage at
        <dot_path>. The generated file can be run through the 'dot' command to
        create an image file of the conveyance graph.

        Args:
            dot_path (string): path where the encoded conveyance graph will be
                written

        Examples: 
            ConveyanceGraph.generate_graph_dot(<dot_path>)
            >>> dot <dot_path> -Tpng -o<image_path>

        """

        dot_str = []
        visited_cells = set()
        queue = self.sources[:]

        # BFS through graph
        while len(queue) > 0:
            cell = queue.pop(0)
            if cell in visited_cells:
                continue
            visited_cells.add(cell)

            nexts = cell.get_nexts()
            queue.extend(nexts)
            
            # Encode cell
            nexts_names = [next.name for next in nexts]
            nexts_str = "\t%s -> { %s }\n" % (cell.name, " ".join(nexts_names))
            dot_str.append(nexts_str) 

        # Write encoded graph to file
        dot_str = "strict digraph {\n" + "".join(dot_str) + "}"
        try:
            with open(dot_path, 'w') as dot_file:
                dot_file.write(dot_str)
        except:
            raise EnvironmentError("Unable to open %s" % (dot_path))
                

    # FIXME change how this is done
    def check_requirements_feasibility(self, requirements):
        """Checks the feasibility of a list of requirements against the ConveyanceGraph

        Args:
            requirements (list): list of requirements to check for feasibility

        """

        subgraphs = []

        # FIXME need to fix this if there are multiple sources
        feasibilities = []
        for requirement in requirements:
            visited_cells = {}
            feasible, cs_root = self._check_requirement_feasibility(requirement.root, 0,
                    self.sources[0], visited_cells, 0)
            feasibilities.append(feasible)

            if feasible == True:
                subgraph = ConveyanceSubgraph(cs_root[0][1])
                subgraphs.append(subgraph)

            print("Requirement '%s' feasibility: %r" % (requirement.name,
                feasible))
        print()

        return feasibilities, subgraphs

    # FIXME need to change conveyancesubgraph node to have a background color
    # for cells. The generic graph object node should have an option for this as
    # well.
    def _check_requirement_feasibility(self, req_node, ops_completed, cell,
            visited_cells, skip):
        # FIXME wording of comment
        """Recursive function to check whether a subset of a requirement is
        satisfied by the ConveyanceGraph

        Args:
            req_node (RequirementNode): requirement node to check
            cell (Cell): cell to check 
            # FIXME change this
            visited_cells (dict): set of cells visited by previous recursive
                calls
        
        """

        # Base cases and early termination
        if cell in visited_cells:
            if visited_cells[cell] == ops_completed:
                return False, None
            else:
                visited_cells[cell] = ops_completed
        else:
            visited_cells[cell] = ops_completed

        if cell.name == "Sink":
            if req_node.op == "TERMINATE":
                cs_node = ConveyanceSubgraphNode(cell)
                return True, [[skip, cs_node]] # Note skip will always be 0
            else:
                return False, None

        # Check if requirement op satisfied
        # FIXME include current node always to check for alternate paths
        req_nexts = [req_node]
        op_satisfied = False
        if req_node.op in cell.ops:
            req_nexts.extend(req_node.nexts)
            op_satisfied = True

        # Iterate over requirements
        reqs_feasible = True
        feasible_paths = []
        for req_next in req_nexts:
            # FIXME create an if statement here to handle case where req_next == req_node
            pass_visited_cells = copy(visited_cells)
            pass_ops_completed = ops_completed
            skip = 1
            if (req_next != req_node):
                pass_visited_cells[cell] += 1
                pass_ops_completed += 1
                skip = 0

            cell_nexts = cell.get_nexts()

            # Iterate each requirement over next cells
            req_feasible = False
            for cell_next in cell_nexts:

                check_feasible, ret_paths = self._check_requirement_feasibility(req_next,
                    pass_ops_completed, cell_next, pass_visited_cells, skip)

                if check_feasible == True:
                    feasible_paths.extend(ret_paths)
                req_feasible = req_feasible or check_feasible

            # FIXME 
            #reqs_feasible = reqs_feasible and req_feasible

            if not op_satisfied:
                reqs_feasible = reqs_feasible and req_feasible
            else:
                if req_next != req_node:
                    reqs_feasible = reqs_feasible and req_feasible

        # Delete this
        cs_paths = []
        if reqs_feasible == True:
            skip_paths = []
            use_paths = []
            for feasible_path in feasible_paths:
                if feasible_path[0] == 1:
                    skip_paths.append(feasible_path)
                else:
                    use_paths.append(feasible_path)

            if len(use_paths) > 0:
                use_cs_node = ConveyanceSubgraphNode(cell) 
                use_cs_node.nexts = [use_path[1] for use_path in use_paths]
                cs_paths.append([skip, use_cs_node])

            if len(skip_paths) > 0:
                skip_cs_node = ConveyanceSubgraphNode(cell)
                skip_cs_node.nexts = [skip_path[1] for skip_path in skip_paths]
                cs_paths.append([skip, skip_cs_node])
        else:
            cs_paths = None

        return reqs_feasible, cs_paths

#def _check_requirement_feasibility(self, req_node, ops_completed, cell, visited_cells):
        # FIXME wording of comment
        """Recursive function to check whether a subset of a requirement is
        satisfied by the ConveyanceGraph

        Args:
            req_node (RequirementNode): requirement node to check
            cell (Cell): cell to check 
            # FIXME change this
            visited_cells (dict): set of cells visited by previous recursive
                calls
        
        """

        """
        # Base cases and early termination
        if cell in visited_cells:
            if visited_cells[cell] == ops_completed:
                return False
            else:
                visited_cells[cell] = ops_completed
        else:
            visited_cells[cell] = ops_completed

        if cell.name == "Sink":
            if req_node.op == "TERMINATE":
                cs_node = ConveyanceSubgraphNode(cell)
                return True, cs_node
            else:
                return False, None

        # Check if requirement op satisfied
        # FIXME include current node always to check for alternate paths
        req_nexts = [req_node]
        op_satisfied = False
        if req_node.op in cell.ops:
            req_nexts.extend(req_node.nexts)
            #visited_cells[cell] += 1
            #ops_completed += 1
            op_satisfied = True

        # Iterate over requirements
        reqs_feasible = True
        cs_node = ConveyanceSubgraphNode(cell)
        cs_node_nexts = []
        for req_next in req_nexts:
            # FIXME create an if statement here to handle case where req_next == req_node
            pass_visited_cells = copy(visited_cells)
            pass_ops_completed = ops_completed
            if (req_next != req_node):
                pass_visited_cells[cell] += 1
                pass_ops_completed += 1

            cell_nexts = cell.get_nexts()

            # Iterate each requirement over next cells
            req_feasible = False
            for cell_next in cell_nexts:

                # FIXME Return a list of ret_nodes
                check_feasible, ret_node = self._check_requirement_feasibility(req_next,
                    pass_ops_completed, cell_next, pass_visited_cells)

                if check_feasible == True:
                    cs_node_nexts.append(ret_node)
                req_feasible = req_feasible or check_feasible

            # FIXME 
            #reqs_feasible = reqs_feasible and req_feasible

            if not op_satisfied:
                reqs_feasible = reqs_feasible and req_feasible
            else:
                if req_next != req_node:
                    reqs_feasible = reqs_feasible and req_feasible

        if reqs_feasible == True:
            cs_node.nexts = cs_node_nexts
        else:
            cs_node = None

        return reqs_feasible, cs_node
"""

class ConveyanceSubgraph():
    def __init__(self, root):
        self.root = root

    def generate_subgraph_dot(self, dot_path):
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
            next_node_str = []
            for next in node.nexts:
                next_node_str.append('"%s" [labels="%s"]' % (next.id, next.name))
            next_node_str = " ".join(next_node_str)
            #next_str = "\t%s -> { %s }\n" % (node.name, " ".join(next_names))
            next_str = '\t{ "%s" [label="%s"] } -> { %s }\n' % (node.id, node.name, next_node_str)
            dot_str.append(next_str)

        dot_str = "strict digraph {\n" + "".join(dot_str) + "}"
        try:
            with open(dot_path, 'w') as dot_file:
                dot_file.write(dot_str)
        except:
            raise EnvironmentError("Unable to open %s" % (dot_path))

class ConveyanceSubgraphNode():
    def __init__(self, ref, nexts=None):
        self.ref = ref
        self.id = uuid4()
        self.name = ref.name
        self.background_color = "white"
        if nexts == None:
            self.nexts = []
        else:
            self.nexts = nexts
