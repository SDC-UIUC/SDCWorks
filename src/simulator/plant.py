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

        self.conv_list = []

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
        
        #pdb.set_trace()

        # Add conveyors to plant
        for conv_datum in parsed_convs:
            conv = Conveyor(**conv_datum)
            self.conv_list.append(conv)    

            # Connect conveyor input
            prev = conv.prevs[0]
            cell_prev = self.cells_dict[prev]
            cell_prev.conv_nexts.append(conv)
            conv.prevs = [cell_prev]

            # Connect conveyor output
            next = conv.nexts[0]
            cell_next = self.cells_dict[next]
            cell_next.conv_prevs.append(conv)
            conv.nexts = [cell_next]

            self.add_graph_edges(cell_prev.name, cell_next.name)

            """
            for i, prev in enumerate(conv.prevs):
                cell_prev = self.cells_dict[prev]
                cell_prev.nexts.append(conv)
                conv.prevs[i] = cell_prev

            for i, next in enumerate(conv.nexts):
                cell_next = self.cells_dict[next]
                cell_next.prevs.append(conv)
                conv.nexts[i] = cell_next

            for prev in conv.prevs:
                for next in conv.nexts:
                    self.add_graph_edges(prev, next)
            """

    # FIXME to return data instead
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

                cell.update(delta_time)

                # Log cell data
                if logging:
                    log = cell.log()
                    logs.append(log)

                # Append prev cells to queue
                if cell.prevs:
                    for prev in cell.prevs:
                        queue.append(prev)

        log_str = None
        if logging:
            log_str = '\n'.join(logs)

        return log_str

