from copy import copy
from datetime import datetime
from simulator.plant import Plant
from simulator.requirements import Requirements
import os, sys

import pdb

class Simulator:
    def __init__(self, plant, requirements, algorithm, directory):
        self.plant = plant
        self.requirements = requirements
        self.algorithm = algorithm

        # Create directories
        self.dot_dir = os.path.join(directory, "dot")
        if not os.path.exists(self.dot_dir):
            os.makedirs(dot_dir)

        self.png_dir = os.path.join(directory, "png")
        if not os.path.exists(self.png_dir):
            os.makedirs(png_dir)

        self.log_dir = os.path.join(directory, "log")
        if not os.path.exists(self.log_dir):
            os.makedirs(log_dir)

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

        # Algorithm output
        for req_paths in algorithm.reqs_paths:
            req_paths_file = "path-%s" % (req_paths.name)
            req_paths_dot_path = os.path.join(self.dot_dir, req_paths_file + ".dot")
            req_paths_png_path = os.path.join(self.png_dir, req_paths_file + ".png")
            req_paths.generate_output_files(req_paths_dot_path, req_paths_png_path)

        # Check if plant satisfies requirements
        self._check_requirements_feasibilities()

        # Update plant's control table
        self.algorithm.initialize_routing_tables()

        # FIXME edit this 
        for source in self.plant.cells["source"]:
            source.set_requirements(self.requirements)

    def _check_requirements_feasibilities(self):
        # Check each requirement for feasibility
        infeasible = []
        for requirement in self.requirements:
            visited_cells = {}
            sources = self.plant.cells["source"]
            for source in sources:
                feasible = self._check_requirement_feasibility(requirement.root, 
                                                               source,
                                                               visited_cells, 0)
            
            if not feasible:
                infeasible.append(requirement.name)

        # Check if there are any infeasible requirements
        if len(infeasible) > 0:
            err_str = ", ".join(infeasible)
            raise AssertionError("The following requirements are infeasible: " +
                    err_str)
                    
    # FIXME change visited to Counter type
    def _check_requirement_feasibility(self, req, cell, visited, num_ops):
        # Check if cell visited 
        if cell in visited:
            if visted[cell] == num_ops:
                return False
        visited[cell] = num_ops

        # Check if reached end
        if cell.type == "sink":
            if req.op == "TERMINATE":
                return True
            else:
                return False

        # Check if requirement operation satisfied
        req_nexts = [req]
        if not cell.type is "conv" and req.op in cell.ops:
            req_nexts = req.get_nexts()

        # Iterate over all next requirements
        reqs_feasible = True
        for req_next in req_nexts:
            visited_param = copy(visited)
            num_ops_param = num_ops
            if not req_next is req:
                visited_param[cell] += 1
                num_ops_param += 1

            # Iterate over all next cells
            req_feasible = False
            for cell_next in cell.get_nexts():
                check_feasible = \
                    self._check_requirement_feasibility(req_next, cell_next, 
                                                        visited_param,
                                                        num_ops_param)
                req_feasible = req_feasible or check_feasible

            # Accumulate feasibilities
            reqs_feasible = reqs_feasible and req_feasible

        return reqs_feasible

    def simulate(self, end_time, delta_time):
        print("Starting simulation")

        log_file = "log_" + datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        log_path = os.path.join(self.log_dir, log_file)

        time = 0
        while (time + delta_time <= end_time):
            log_str = self.plant.update(delta_time)
            time += delta_time

            # Write log to file
            if log_str:
                log_str = "Time: %f\n##########\n" % (time) + log_str + "##########\n\n"
                with open(log_path, 'a') as log_file:
                    log_file.write(log_str)

        print("Ending simulation")

