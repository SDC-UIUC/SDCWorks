from collections import OrderedDict
from copy import copy
from custom.widget import CustomWidget
from generic.controller import GenericController
from generic.graph import GenericGraph, GenericGraphNode
import os, pickle

import pdb

class CustomController(GenericController):
    def __init__(self, requirements, plant, metrics):
        self._requirements = requirements
        self.metrics = metrics

        # All cells
        self.cells = plant.cells

        self._widgets = {}
        self._feasible_graphs = self._generate_feasibility_graphs(requirements)

        # Instantiation
        self._req_keys = list(requirements.keys())
        self._req_which = 0

        # Completed widgets
        self._completed = OrderedDict()
        for name in requirements.keys():
            self._completed[name] = {}
            
    def generate_output_files(self, dot_dir, graph_dir):
        for req_name, feasible_graph in self._feasible_graphs.items():
            fg_file = "fg-%s" % (req_name)
            fg_dot_path = os.path.join(dot_dir, fg_file + ".dot")
            fg_png_path = os.path.join(graph_dir, fg_file + ".png")
            feasible_graph.generate_output_files(fg_dot_path, fg_png_path)

    def log_statistics(self):
        req_str = ""
        for req_name, req_dict in self._completed.items():
            req_str += "Requirement name: %s\n" % (req_name)
            for path, widgets in req_dict.items():
                req_str += "\t%s: %d\n" % (str(path), len(widgets))
            req_str += "\n"

        return req_str
            
    def update(self, cur_time):
        # Update all cell states
        self._update_one(cur_time)        

        # Compute SPF for all requirements
        for req_name, fg in self._feasible_graphs.items():
            visited = set()
            self._compute_spf(req_name, fg.root, visited)

        # Update all cell states
        self._update_two(cur_time)

    def _update_one(self, cur_time):
       for _, cell in self.cells["all"].items():
           cell.set_cost()

    def _compute_spf(self, req_name, fg_node, visited):
        if fg_node.id in visited:
            return
        visited.add(fg_node.id)

        cell = fg_node.reference
        nexts = fg_node.get_nexts()
        if not nexts:
            fg_node.next_transfer = None
            return (cell.cost, fg_node)

        next_costs = []
        for next in nexts:
            next_cost = self._compute_spf(req_name, next, visited)
            next_costs.append(next_cost)

        # Select next with minimum weight
        func = lambda nc: nc[0]
        next_cost, next_fg = min(next_costs, key=func)
        fg_node.next_transfer = next_fg

        return (cell.cost + next_cost, fg_node)

    def _update_two(self, cur_time):
       for cell_id, cell in self.cells["all"].items():
            # Handle cell actions
            if cell.type == "cell":
                widget = cell.head()
                if cell.status == "idle":
                    if isinstance(widget, CustomWidget):
                        widget_op = widget.feasible_ptr.op 
                        cell.op_start_time = cur_time
                        cell.status = "operational"
                        cell.action = widget_op.name
                    else:
                        cell.action = "NOP"

                if cell.status == "operational":
                    widget_op = widget.feasible_ptr.op
                    if cur_time - cell.op_start_time >= widget_op.duration:
                        widget.completed_ops.append(widget.feasible_ptr.op)
                        cell.status = "waiting"

                if cell.status == "waiting":
                    if self._try_transfer(cell):
                        cell.action = "transfer"
                        cell.status = "idle"
                    else:
                        cell.action = "NOP"

                # Transfer from conveyor to cell
                if cell.can_enqueue():
                    func = lambda c: c.wait_time
                    conv = max(cell.get_prevs(), key=func)
                    if self._try_transfer(conv):
                        conv.action = "transfer"

            # Handle conveyor actions
            elif cell.type == "conveyor":
                widget = cell.head()
                if isinstance(widget, CustomWidget):
                    cell.wait_time += 1
                    if cell.action == "move":
                        cell.action = "NOP"
                else:
                    cell.wait_time = 0
                    cell.action = "move"

            # Handle source actions
            elif cell.type == "source":
                cell.widget_inst = None
                cell.action = "NOP"
                if isinstance(cell.head(), CustomWidget):
                    if self._try_transfer(cell):
                        cell.action = "transfer"

                if cell.action == "NOP" and cell.can_enqueue():
                    cell.action = "instantiate"
                    req_name = self._req_keys[self._req_which]
                    self._req_which = (self._req_which + 1) % len(self._req_keys)

                    # Instantiate new widget
                    new_widget = CustomWidget(req_name)
                    new_widget.feasible_ptr = self._feasible_graphs[req_name].root
                    new_widget.processing_time = cur_time
                    self._widgets[new_widget.id] = new_widget
                    cell.widget_inst = new_widget

                    # Update metrics data
                    self.metrics.update_metrics_instantiation(new_widget)

            # Handle sink actions
            elif cell.type == "sink":
                widget = cell.head()
                if isinstance(widget, CustomWidget):
                    cell.action = "terminate"
                    self._widgets.pop(widget.id)
                    widget.plant_path.append(widget.feasible_ptr.name)
                    widget.processing_time = cur_time - widget.processing_time
                    
                    # Add widget to completed list
                    req_dict = self._completed[widget.req_name]
                    path = tuple(widget.plant_path)
                    if path not in req_dict:
                        req_dict[path] = [widget]
                    else:
                        req_dict[path].append(widget)
                    
                    # Update metrics data
                    self.metrics.update_metrics_termination(widget)

                else:
                    cell.action = "NOP"
                    
                # Transfer from conveyor to cell
                if cell.can_enqueue():
                    func = lambda c: c.wait_time
                    conv = max(cell.get_prevs(), key=func)
                    if self._try_transfer(conv):
                        conv.action = "transfer"
                
    def _try_transfer(self, cell):
        widget = cell.head()
        if isinstance(widget, type(None)):
            return False

        next_transfer = widget.feasible_ptr.next_transfer.reference
        if next_transfer.can_enqueue():
            cell.next_transfer = next_transfer
            widget.plant_path.append(widget.feasible_ptr.name)
            widget.feasible_ptr = widget.feasible_ptr.next_transfer
            return True
        else:
            return False

    # FIXME add a master_source/master_sink at some point
    def _generate_feasibility_graphs(self, requirements):
        feasible_graphs = {}
        for name, requirement in requirements.items():
            fg = FeasibilityGraph(requirement.name)

            # FIXME for now have one source
            sources = self.cells["source"]
            assert(len(sources) == 1)
            source = sources[0]

            visited_cells = {}
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
        if not cell.type is "conveyor" and req.op in cell.ops:
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
            fg_node = FeasibilityNode(cell, "NOP", not cell.type is "conveyor")
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

class FeasibilityGraph(GenericGraph):
    def __init__(self, name, root=None):
        super().__init__(name, root)

class FeasibilityNode(GenericGraphNode):
    def __init__(self, reference, op, skip=False):
        super().__init__(reference.name)

        self.reference = reference
        self.next_transfer = None
        self.op = reference.ops[op]

        self.dot_attrs["style"] = "filled"
        if not skip:
            self.dot_attrs["fillcolor"] = "white"
        else:
            self.dot_attrs["fillcolor"] = "ivory4"

