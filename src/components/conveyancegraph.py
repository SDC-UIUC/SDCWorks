from copy import copy

import pdb

class ConveyanceGraph:
    def __init__(self, cells, conns):
        """Links cells and connections together to initialize a ConveyanceGraph
        object

        Args:
            cells (dict): dictionary of {"name": <Cell>}
            conns (dict): dictionary of {"name": <Connection>}

        """

        self.source = None
        self.sink = None

        # Link cells and connections together
        for name, cell in cells.items():
            if name not in conns:
                raise ValueError("No connection found for cell '%s'" % (name))

            cell.conns = conns[name]
            for conn in conns[name]:
                conn.endpoints.add(cell)

            if cell.type == "source":
                self.source = cell
            elif cell.type == "sink":
                self.sink = cell

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
        queue = [self.source]

        # BFS through graph
        while len(queue) > 0:
            cell = queue.pop(0)
            if cell in visited_cells:
                continue
            visited_cells.add(cell)

            nexts = cell.get_nexts()
            nexts = list(set(nexts) - visited_cells)
            queue.extend(nexts)
            
            # Encode cell
            nexts_names = [next.name for next in nexts]
            nexts_str = "\t%s -- { %s }\n" % (cell.name, 
                                                   " ".join(nexts_names))
            dot_str.append(nexts_str) 

        # Write encoded graph to file
        dot_str = "graph {\n" + "".join(dot_str) + "}"
        try:
            with open(dot_path, 'w') as dot_file:
                dot_file.write(dot_str)
        except:
            raise EnvironmentError("Unable to open %s" % (dot_path))
                

    def check_requirements_feasibility(self, requirements):
        """Checks the feasibility of a list of requirements against the ConveyanceGraph

        Args:
            requirements (list): list of requirements to check for feasibility

        """

        feasibilities = []
        for requirement in requirements:
            visited_cells = set()
            feasible = self._check_requirement_feasibility(requirement.root,
                    self.source, visited_cells)
            feasibilities.append(feasible)
            print("Requirement '%s' feasibility: %r" % (requirement.name,
                feasible))
        print()

        return feasibilities

    def _check_requirement_feasibility(self, req_node, cell, visited_cells):
        """Recursive function to check whether a subset of a requirement is
        satisfied by the ConveyanceGraph

        Args:
            req_node (RequirementNode): requirement node to check
            cell (Cell): cell to check 
            visited_cells (set): set of cells visited by previous recursive
                calls
        
        """

        # Base cases and early termination
        if cell in visited_cells:
           return False
        visited_cells.add(cell)

        if cell.name == "Sink" and not req_node.op == "END":
            return False
        elif cell.name == "Sink" and req_node.op == "END":
            return True

        # Check if requirement op satisfied
        if req_node.op in cell.ops:
            req_nexts = req_node.nexts
        else:
            req_nexts = [req_node]

        # Iterate over requirements
        reqs_feasible = True
        for req_next in req_nexts:
            pass_visited_cells = copy(visited_cells)
            cell_nexts = cell.get_nexts()
            cell_nexts = list(set(cell_nexts) - visited_cells)

            # Iterate each requirement over next cells
            req_feasible = False
            for cell_next in cell_nexts:
                check_feasible = self._check_requirement_feasibility(req_next, 
                        cell_next, pass_visited_cells)
                req_feasible = req_feasible or check_feasible
            reqs_feasible = reqs_feasible and req_feasible
        
        # Return requirements feasibility
        return reqs_feasible

