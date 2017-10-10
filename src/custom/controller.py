from copy import copy
from custom.widget import Widget
from generic.controller import GenericController
from generic.graph import GenericGraph, GenericGraphNode
import os, pickle

import pdb

class Controller(GenericController):
    def __init__(self, network, requirements):
        self._network = network
        self._requirements = requirements

        self._feasible_graphs = self._generate_feasibility_graphs(requirements)
        self._widgets = {}

        # Instantiation
        self._req_keys = list(requirements.keys())
        self._req_which = 0

        # Rename this to completed
        self._completed = {}
        for name in requirements.keys():
            self._completed[name] = {}

        # Plot variables
        self.ticks_per_hour = 3600.0

        self._total_widgets_plot = []
        self._throughput_plot = {}
        self._throughput_num = {}
        self._end_to_end_plot = {}
        self._end_to_end_sum = {}

        for name in requirements.keys():
            self._throughput_plot[name] = []
            self._throughput_num[name] = 0
            self._end_to_end_plot[name] = []
            self._end_to_end_sum[name] = 0
    
        # Initialize network with controller functions
        network.add_dispatch_command("controller", "notify_completion",
            self.notify_completion)
        network.add_dispatch_command("controller", "notify_enqueue",
            self.notify_enqueue)
        network.add_dispatch_command("controller", "notify_termination",
            self.notify_termination)

        network.add_dispatch_command("controller", "query_instantiate",
           self.query_instantiate)
        network.add_dispatch_command("controller", "query_next",
            self.query_next)
        network.add_dispatch_command("controller", "query_operation",
            self.query_operation)

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

    def notify_completion(self, widget_id, op, time):
        widget = self._widgets[widget_id]
        if not op == "NOP":
            widget.completed_ops.append(op)
        widget.plant_path.append(widget.ptr.name)

        if op == "TERMINATE":
            self._widgets.pop(widget_id)
            widget.ptr = None
            widget.processing_time = time - widget.processing_time
            req_dict = self._completed[widget.req_name]

            path = tuple(widget.plant_path)
            if path not in req_dict:
                req_dict[path] = [widget]
            else:
                req_dict[path].append(widget)

            # Plot data
            self._throughput_num[widget.req_name] += 1
            self._end_to_end_sum[widget.req_name] += widget.processing_time

    def notify_enqueue(self, widget_id):
        widget = self._widgets[widget_id]
        widget.ptr = widget.ptr.best_next

    # TODO check the processing list against requirement 
    def notify_termination(self, widget_id, op):
        widget = self._widgets.pop(widget_id)
        widget.ptr = None
        self._completed[widget.req_name] = req_dict

    def query_instantiate(self, time):
        req_name = self._req_keys[self._req_which]
        self._req_which = (self._req_which + 1) % len(self._req_keys)

        widget = Widget(req_name)
        widget.ptr = self._feasible_graphs[req_name].root
        widget.processing_time = time
        self._widgets[widget.id] = widget
        return widget, widget.ptr.op

    def query_next(self, widget_id):
        widget = self._widgets[widget_id]
        next = widget.ptr.best_next._reference
        return next

    def query_operation(self, widget_id):
        widget = self._widgets[widget_id]
        return widget.ptr.op

    def save_statistics(self, data_dir):
        # Save total number of widgets
        data_path = os.path.join(data_dir, "total_widgets.pickle")
        with open(data_path, 'wb') as data_file:
            pickle.dump(self._total_widgets_plot, data_file)  

        # Save widgets completed per hour
        data_path = os.path.join(data_dir, "throughput.pickle")
        with open(data_path, 'wb') as data_file:
            pickle.dump(self._throughput_plot, data_file)

        # Save end-to-end average
        data_path = os.path.join(data_dir, "end-to-end.pickle")
        with open(data_path, 'wb') as data_file:
            pickle.dump(self._end_to_end_plot, data_file) 

    # TODO this is a user defined function to set the weights of each of the
    # nodes. This will be need to be passed in by the user
    def set_weights(self, cell):
        #pass
        
        weight = 0
        for elem in cell._reference._queue:
            if not elem is None:
                weight += 1

        cell.weight = weight
        
    def update_statistics(self, time):
        # Total number of widgets in the system
        total_widgets = [time, len(self._widgets)]
        self._total_widgets_plot.append(total_widgets)

        # Widgets completed per hour
        for req_id, req_dict in self._completed.items():
            if time <= 0:
                req_throughput = 0
            else:
                req_throughput = self._throughput_num[req_id] / time * self.ticks_per_hour
            throughput = [time, req_throughput]
            self._throughput_plot[req_id].append(throughput)

        # End-to-end average
        for req_id, req_dict in self._completed.items():
            if len(req_dict) == 0:
                end_to_end_average = 0
            else:
                end_to_end_average = self._end_to_end_sum[req_id] / self._throughput_num[req_id]
            end_to_end = [time, end_to_end_average]
            self._end_to_end_plot[req_id].append(end_to_end)
        
    def update(self):
        for req_name, fg in self._feasible_graphs.items():
            visited = set()
            self._update_cell_control(fg.root, visited)

    def _update_cell_control(self, cell, visited):
        if cell.id in visited:
            return
        visited.add(cell.id)

        # Set the weight of the cell
        self.set_weights(cell)

        # Recurse through FeasibleGraph
        nexts = cell.get_nexts()
        if not nexts:
            cell.best_next = None
            return (cell.weight, cell)

        next_weights = []
        for next in nexts:
           next_weight = self._update_cell_control(next, visited)
           next_weights.append(next_weight)

        # Select next with minimum weight
        next_weights.sort(key=lambda idx: idx[0])
        best_weight, best_next = next_weights[0]
        cell.best_next = best_next

        return (cell.weight + best_weight, cell)

    # FIXME add a master_source/master_sink at some point
    def _generate_feasibility_graphs(self, requirements):
        feasible_graphs = {}
        for name, requirement in requirements.items():
            fg = FeasibilityGraph(name)

            visited_cells = {}

            # FIXME for now have one source
            sources = self._network.process_network_command("plant", "query_cells",
                    "source")
            #sources = self.plant.cells["source"]
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

class FeasibilityGraph(GenericGraph):
    def __init__(self, name, root=None):
        super().__init__(name, root)

class FeasibilityNode(GenericGraphNode):
    def __init__(self, reference, op, skip=False):
        super().__init__(reference.name)

        self._reference = reference
        self.best_next = None
        self.op = reference.ops[op]
        self.weight = 0

        self.dot_attrs["style"] = "filled"
        if not skip:
            self.dot_attrs["fillcolor"] = "white"
        else:
            self.dot_attrs["fillcolor"] = "ivory4"

