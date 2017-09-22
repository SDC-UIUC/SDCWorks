from abc import ABC, abstractmethod
from copy import copy
from generic.graph import Graph, GraphNode

import pdb

class Algorithm(ABC):
    def __init__(self, plant, requirements):
        self.plant = plant
        self.requirement = requirement

    @abstractmethod
    def initialize_routing_tables(self):
        pass

    @abstractmethod
    def update_routing_tables(self):
        pass

    # FIXME
    def generate_all_feasible_paths(self):
        #pdb.set_trace()

        all_paths = []
        for requirement in self.requirements:
            req_paths = []
            cg = ConveyanceGraph(requirement.name, req_paths)
            visited_cells = {}
            sources = self.plant.cells["source"]
            for source in sources:
                paths = self.generate_feasible_paths(requirement.root, source, 
                                                     visited_cells, 0, cg)
                req_paths.extend(paths)
            all_paths.append(cg) 

        return all_paths
                
    def generate_feasible_paths(self, req, cell, visited, num_ops, cg):
        # Check if cell visited
        if cell in visited:
            if visited[cell] == num_ops:
                return [None]
        visited[cell] = num_ops

        # Check if end reached
        if cell.type == "sink":
            if req.op == "TERMINATE":
                cg_node = ConveyanceNode(cell, req.op)
                cg.add_graph_nodes(cg_node)
                return [cg_node]
            else:
                return [None]

        # Check if requirement operation satisfied
        req_nexts = []
        req_sat = False
        if req.op in cell.ops:
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

            for cell_next in cell.get_nexts(cells=True):
                feasible_paths = \
                    self.generate_feasible_paths(req_next, cell_next, 
                                                 visited_param,
                                                 num_ops_param, cg)

                # Prepend current node to returned paths
                for feasible_path in feasible_paths:
                    if not feasible_path:
                        continue

                    if skip_req:
                        cg_node = ConveyanceNode(cell, "PASS", skip_req)
                    else:
                        cg_node = ConveyanceNode(cell, req.op, skip_req)
                    cg.add_graph_nodes(cg_node)
                    cg.add_graph_edges(cg_node.name, feasible_path.name)
                    paths.append(cg_node)

            return paths

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

class ConveyanceGraph(Graph):
    def __init__(self, name, root):
        super().__init__(name, root)

class ConveyanceNode(GraphNode):
    def __init__(self, ref, op, skip=False, nexts=None):
        super().__init__(ref.name, nexts)

        #self.id = uuid4()
        self.ref = ref
        self.op = op
        self.weight = 0

        if not skip:
            self.dot_attrs["fillcolor"] = "white"
        else:
            self.dot_attrs["fillcolor"] = "gray"
