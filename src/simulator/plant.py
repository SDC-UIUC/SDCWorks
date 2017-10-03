from collections import deque
from datetime import datetime
from parser.parser import parse_plant
from generic.graph import Graph
from simulator.cells import *

from copy import copy
from uuid import uuid4

import os

import pdb

class Plant(Graph):
    def __init__(self, plant_yaml, network):
        """Builds a conveyance graph from the description provided in the input
        file

        Args:
            graph_yaml (string): path to the YAML file with the graph
                description           

        """

        super().__init__("Plant")
        self.network = network

        self.cells = {
            "source": [],
            "cell": [],
            "sink": [],
        }
        self.cells_dict = {}

        # Parse graph YAML
        parsed_cells, parsed_convs = parse_plant(plant_yaml)

        # Adds cells to plant
        cell_init = { "source": Source, "cell": Cell, "sink": Sink }
        for type, cell_data in parsed_cells.items():
            for cell_datum in cell_data:
                cell = cell_init[type](network=network, **cell_datum)
                self.cells_dict[cell.name] = cell
                self.cells[type].append(cell)
                self.add_graph_nodes(cell)

        # Add conveyors to plant
        for conv_datum in parsed_convs:
            prevs = conv_datum.pop("prev")
            nexts = conv_datum.pop("next")
            conv = Conveyor(network=network, **conv_datum)
            self.add_graph_nodes(conv)

            # Connect conveyor previous
            for prev in prevs:
                prev = self.cells_dict[prev]
                self.add_graph_edges(prev, conv)

            # Connect conveyor next
            for next in nexts:
                next = self.cells_dict[next]
                self.add_graph_edges(conv, next)

        # Initialize network with plant function
        network.add_dispatch_command("plant", "query_cells",
            self.query_cells)
                
    def check_feasibilities(self, requirements):
        # Check each requirement for feasibility
        infeasible = []
        for requirement in requirements:
            visited_cells = {}
            sources = self.cells["source"]
            for source in sources:
                feasible = self._check_feasibility(requirement.root, 
                                                   source, visited_cells, 0)
            
            if not feasible:
                infeasible.append(requirement.name)

        # Check if there are any infeasible requirements
        if len(infeasible) > 0:
            err_str = ", ".join(infeasible)
            raise AssertionError("The following requirements are infeasible: " +
                    err_str)
                    
    # FIXME use cell.id to check for visited rather than cell as key
    def _check_feasibility(self, req, cell, visited, num_ops):
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
                    self._check_feasibility(req_next, cell_next, 
                                            visited_param, num_ops_param)
                req_feasible = req_feasible or check_feasible

            # Accumulate feasibilities
            reqs_feasible = reqs_feasible and req_feasible

        return reqs_feasible
    
    def query_cells(self, types=None):
        cells = []
        if not types:
            for item in self.cells.items():
                cells.extend(item)
        else:
            for type in types:
                cells.extend(self.cells[type])

        return cells

    def update(self, cur_time):
        queue = deque()
        visited = set()

        # Add all sinks to queue
        sinks = self.cells["sink"]
        for sink in sinks:
            queue.append(sink)

        # Perform reverse BFS
        while len(queue) > 0:
            n = len(queue)
            for i in range(n):
                cell = queue.popleft()

                if cell.id in visited:
                    continue
                visited.add(cell.id)

                cell.update(cur_time)

                # Append prev cells to queue
                for prev in cell.get_prevs():
                    queue.append(prev)

    def log(self):
        queue = deque()
        visited = set()

        # Add all sinks to queue
        sinks = self.cells["sink"]
        for sink in sinks:
            queue.append(sink)

        # Perform reverse BFS
        logs = []
        while len(queue) > 0:
            n = len(queue)
            for i in range(n):
                cell = queue.popleft()

                if cell.id in visited:
                    continue
                visited.add(cell.id)

                log = cell.log()
                logs.append(log)

                # Append prev cells to queue
                for prev in cell.get_prevs():
                    queue.append(prev)

        return '\n'.join(logs)

