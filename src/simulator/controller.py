from simulator.widgets import VirtualWidget
import matplotlib.pyplot as plt
import numpy as np
import os, pickle

import pdb

class Controller():
    def __init__(self, network, requirements):
        self._network = network
        self.requirements = requirements

        self._control_table = None
        self.requirement_keys = None
        self._widgets = {}

        # Instantiation
        self.req_which = 0

        # Rename this to completed
        self._completed_widgets = {}
        for requirement in self.requirements:
            self._completed_widgets[requirement.id] = {}

        # Plot variables
        self.ticks_per_hour = 3600.0

        self._total_widgets_plot = []
        self._throughput_plot = {}
        self._throughput_num = {}
        self._end_to_end_plot = {}
        self._end_to_end_sum = {}

        for requirement in self.requirements:
            self._throughput_plot[requirement.id] = []
            self._throughput_num[requirement.id] = 0
            self._end_to_end_plot[requirement.id] = []
            self._end_to_end_sum[requirement.id] = 0
    
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

    def initialize_control_table(self, feasible_graphs):
        self._control_table = feasible_graphs
        self.requirement_keys = [req.id for req in self.requirements]
        self.update_control_table()

    def log_statistics(self):
        req_str = ""
        for req_id, req_dict in self._completed_widgets.items():

            # FIXME
            for requirement in self.requirements:
                if requirement.id == req_id:
                    req_name = requirement.name
                    break

            req_str += "Requirement name: %s\n" % (req_name)
            for path, widgets in req_dict.items():
                req_str += "\t%s: %d\n" % (str(path), len(widgets))
            req_str += "\n"

        return req_str

    def notify_completion(self, widget_id, op, time):
        widget = self._widgets[widget_id]
        if not op == "NOP":
            widget.completed_ops.append(op)
        widget.path.append(widget.ptr.name)

        if op == "TERMINATE":
            self._widgets.pop(widget_id)
            widget.ptr = None
            widget.processing_time = time - widget.processing_time
            req_dict = self._completed_widgets[widget.req_id]

            path = tuple(widget.path)
            if path not in req_dict:
                req_dict[path] = [widget]
            else:
                req_dict[path].append(widget)

            # Plot data
            self._throughput_num[widget.req_id] += 1
            self._end_to_end_sum[widget.req_id] += widget.processing_time

    def notify_enqueue(self, widget_id):
        widget = self._widgets[widget_id]
        widget.ptr = widget.ptr.best_next

    # TODO check the processing list against requirement 
    def notify_termination(self, widget_id, op):
        widget = self._widgets.pop(widget_id)
        widget.ptr = None
        self._completed_widgets[widget.req_id] = req_dict

    # TODO remove this
    def plot_statistics(self):
        # Plot total number of widgets at any given time
        self._total_widgets_plot = np.array(self._total_widgets_plot)
        widgets = self._total_widgets_plot[:, 0]
        time = self._total_widgets_plot[:, 1]

        plt.plot(widgets, time)
        plt.show()

    # FIXME spawns always
    def query_instantiate(self, time):
        req_id = self.requirement_keys[self.req_which]
        self.req_which = (self.req_which + 1) % len(self.requirements)

        widget = VirtualWidget(req_id)
        widget.ptr = self._control_table[req_id].root
        widget.processing_time = time
        self._widgets[widget.id] = widget
        return widget.id, widget.ptr.op

    def query_next(self, widget_id):
        widget = self._widgets[widget_id]
        next = widget.ptr.best_next.ref
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
        for elem in cell.ref._queue:
            if not elem is None:
                weight += 1

        cell.weight = weight
        
    def update_statistics(self, time):
        # Total number of widgets in the system
        total_widgets = [time, len(self._widgets)]
        self._total_widgets_plot.append(total_widgets)

        # Widgets completed per hour
        for req_id, req_dict in self._completed_widgets.items():
            if time <= 0:
                req_throughput = 0
            else:
                req_throughput = self._throughput_num[req_id] / time * self.ticks_per_hour
            throughput = [time, req_throughput]
            self._throughput_plot[req_id].append(throughput)

        # End-to-end average
        for req_id, req_dict in self._completed_widgets.items():
            if len(req_dict) == 0:
                end_to_end_average = 0
            else:
                end_to_end_average = self._end_to_end_sum[req_id] / self._throughput_num[req_id]
            end_to_end = [time, end_to_end_average]
            self._end_to_end_plot[req_id].append(end_to_end)
        
    # FIXME rename this
    def update_control_table(self):
        for req_id, graph in self._control_table.items():
            visited = set()
            self._update_cell_control(graph.root, visited)

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

        

        


