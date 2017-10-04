from copy import copy
from datetime import datetime
from generic.graph import Graph, GraphNode

import os, sys

import pdb

class Simulator:
    def __init__(self, plant, controller, requirements, directory):
        self.plant = plant
        self.controller = controller
        self.requirements = requirements

        # Create directories
        self.dot_dir = os.path.join(directory, "dot")
        if not os.path.exists(self.dot_dir):
            os.makedirs(self.dot_dir)

        self.png_dir = os.path.join(directory, "png")
        if not os.path.exists(self.png_dir):
            os.makedirs(self.png_dir)

        self.log_dir = os.path.join(directory, "log")
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        # Plant output
        plant_dot_path = os.path.join(self.dot_dir, "plant.dot")
        plant_png_path = os.path.join(self.png_dir, "plant.png")
        self.plant.generate_output_files(plant_dot_path, plant_png_path)

        # Requirement output
        for requirement in self.requirements:
            req_file = "requirement-%s" % (requirement.name)
            req_dot_path = os.path.join(self.dot_dir, req_file + ".dot")
            req_png_path = os.path.join(self.png_dir, req_file + ".png")
            requirement.generate_output_files(req_dot_path, req_png_path)

        # Check if plant satisfies requirements
        self.plant.check_feasibilities(requirements)

        # Generate all feasible paths
        feasible_graphs = self._generate_feasibility_graphs()
        for req_id, feasible_graph in feasible_graphs.items():
            fg_file = "fg-%s" % (req_id)
            fg_dot_path = os.path.join(self.dot_dir, fg_file + ".dot")
            fg_png_path = os.path.join(self.png_dir, fg_file + ".png")
            feasible_graph.generate_output_files(fg_dot_path, fg_png_path)

        # Initialize controller control table
        self.controller.initialize_control_table(feasible_graphs)

        """
        for source in self.plant.cells["source"]:
            source.set_requirements(self.requirements)
        """
    
    # FIXME add a master_source/master_sink at some point
    # FIXME move this over to controller at some point
    def _generate_feasibility_graphs(self):
        feasible_graphs = {}
        for requirement in self.requirements:
            fg = FeasibilityGraph(requirement.name)

            visited_cells = {}

            sources = self.plant.cells["source"]

            # FIXME for now have one source
            assert(len(sources) == 1)
            source = sources[0]

            root = self._generate_feasible_graph(requirement.root, source,
                                                 visited_cells, 0, fg)
            assert(len(root) == 1)
            fg.root = root[0]
            feasible_graphs[requirement.name] = fg

        return feasible_graphs

    def _generate_feasible_graph(self, req, cell, visited, num_ops, fg):
        # Check if cell visited
        if cell in visited:
            if visited[cell] == num_ops:
                return None
        visited[cell] = num_ops

        # Check if end reached
        if cell.type == "sink":
            if req.op == "TERMINATE":
                fg_node = FeasibilityNode(cell, req.op)
                fg.add_graph_nodes(fg_node)
                return [fg_node]
            else:
                return None

        # Check if requirement operation satisfied
        req_nexts = [req]
        req_sat = False
        if not cell.type is "conv" and req.op in cell.ops:
            req_nexts.extend(req.get_nexts())
            req_sat = True

        # Iterate over all next requirements requirements
        feasible_use_graphs = []
        feasible_skip_graphs = []
        for req_next in req_nexts:
            visited_param = copy(visited)
            num_ops_param = num_ops
            skip_req = True
            if not req_next is req:  
                visited_param[cell] += 1
                num_ops_param += 1
                skip_req = False

            for next in cell.get_nexts():
                feasible_graph = \
                    self._generate_feasible_graph(req_next, next, 
                                                  visited_param,
                                                  num_ops_param, fg)

                if not feasible_graph:
                    continue

                if skip_req:
                    feasible_skip_graphs.extend(feasible_graph)
                else:
                    feasible_use_graphs.extend(feasible_graph)

        feasible_graphs = []
        if len(feasible_skip_graphs) > 0:
            fg_node = FeasibilityNode(cell, "NOP", not cell.type is "conv")
            fg.add_graph_nodes(fg_node)
            
            for graph in feasible_skip_graphs:
                fg.add_graph_edges(fg_node, graph)
            feasible_graphs.append(fg_node)
            
        if len(feasible_use_graphs) > 0:
            fg_node = FeasibilityNode(cell, req.op)
            fg.add_graph_nodes(fg_node)

            for graph in feasible_use_graphs:
                fg.add_graph_edges(fg_node, graph)
            feasible_graphs.append(fg_node)

        if len(feasible_graphs) == 0:
            return None 
        return feasible_graphs

    def simulate(self, end_time, delta_time):
        print("Starting simulation")

        log_file = "log_" + datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        log_path = os.path.join(self.log_dir, log_file)

        time = -delta_time
        while (time < end_time):
            time += delta_time
            self.plant.update(time)

            # Log and write to file
            log_str = self.plant.log() 
            log_str = "Time: %f\n##########\n" % (time) + log_str + "##########\n\n"
            with open(log_path, 'a') as log_file:
                log_file.write(log_str)

        print("Ending simulation")

class FeasibilityGraph(Graph):
    def __init__(self, name, root=None):
        super().__init__(name, root)

class FeasibilityNode(GraphNode):
    def __init__(self, ref, op, skip=False):
        super().__init__(ref.name)

        self.ref = ref
        self.best_next = None
        self.op = (op, ref.ops[op])
        self.weight = 0

        self.dot_attrs["style"] = "filled"
        if not skip:
            self.dot_attrs["fillcolor"] = "white"
        else:
            self.dot_attrs["fillcolor"] = "ivory4"

