from collections import deque
from datetime import datetime
from parser.parser import parse_plant
from generic.graph import Graph
from simulator.cells import *

from copy import copy
from uuid import uuid4

import os

import pdb

# FIXME Rename this to Plant and rename ConveyanceSubgraph to ConveyanceGraph
class Plant(Graph):
    def __init__(self, plant_yaml):
        """Builds a conveyance graph from the description provided in the input
        file

        Args:
            graph_yaml (string): path to the YAML file with the graph
                description           

        """

        super().__init__("Plant")

        self.cells = {
            "source": [],
            "cell": [],
            "sink": [],
        }
        self.cells_dict = {}

        self._control_table = {}

        # Parse graph YAML
        parsed_cells, parsed_convs = parse_plant(plant_yaml)

        # Adds cells to plant
        cell_init = { "source": Source, "cell": Cell, "sink": Sink }
        for type, cell_data in parsed_cells.items():
            for cell_datum in cell_data:
                cell = cell_init[type](**cell_datum)
                self.cells_dict[cell.name] = cell
                self.cells[type].append(cell)
                self.add_graph_nodes(cell)
                self._control_table[cell.id] = {}

        # Add conveyors to plant
        for conv_datum in parsed_convs:
            prevs = conv_datum.pop("prev")
            nexts = conv_datum.pop("next")
            conv = Conveyor(**conv_datum)
            self.add_graph_nodes(conv)
            self._control_table[conv.id] = {}

            # Connect conveyor previous
            for prev in prevs:
                prev = self.cells_dict[prev]
                self.add_graph_edges(prev, conv)

            # Connect conveyor next
            for next in nexts:
                next = self.cells_dict[next]
                self.add_graph_edges(conv, next)
                
    def update_control_table(self, node_name, key, value):
        node_control = self._control_table[node_name]
        node_control[key] = value

    def update(self, delta_time, logging=True):
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

                if cell in visited:
                    continue
                visited.add(cell)

                cell_control_table = self._control_table[cell.id]
                cell.update(delta_time, cell_control_table)

                # Log cell data
                if logging:
                    log = cell.log()
                    logs.append(log)

                # Append prev cells to queue
                for prev in cell.get_prevs():
                    queue.append(prev)

        log_str = None
        if logging:
            log_str = '\n'.join(logs)

        return log_str

