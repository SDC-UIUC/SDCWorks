from simulator.widgets import VirtualWidget

import matplotlib.pyplot as plt
import numpy as np

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
        self._total_widgets_per_time = []

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
        self.requirement_keys = list(self._control_table.keys())
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
                req_str += "\t%s: %d\n\n" % (str(path), len(widgets))

        return req_str

    def notify_completion(self, widget_id, op):
        widget = self._widgets[widget_id]
        if not op == "NOP":
            widget.completed_ops.append(op)
        widget.path.append(widget.ptr.name)

        if op == "TERMINATE":
            self._widgets.pop(widget_id)
            widget.ptr = None
            req_dict = self._completed_widgets[widget.req_id]

            path = tuple(widget.path)
            if path not in req_dict:
                req_dict[path] = [widget]
            else:
                req_dict[path].append(widget)

    def notify_enqueue(self, widget_id):
        widget = self._widgets[widget_id]
        widget.ptr = widget.ptr.best_next

    # TODO check the processing list against requirement 
    def notify_termination(self, widget_id, op):
        widget = self._widgets.pop(widget_id)
        widget.ptr = None
        self._completed_widgets[widget.req_id] = req_dict

    def plot_statistics(self):
        # Plot total number of widgets at any given time
        self._total_widgets_per_time = np.array(self._total_widgets_per_time)
        widgets = self._total_widgets_per_time[:, 0]
        time = self._total_widgets_per_time[:, 1]

        plt.plot(widgets, time)
        plt.show()


    # FIXME spawns always
    def query_instantiate(self):
        req_id = self.requirement_keys[self.req_which]
        self.req_which = (self.req_which + 1) % len(self.requirements)

        widget = VirtualWidget(req_id)
        widget.ptr = self._control_table[req_id].root
        self._widgets[widget.id] = widget
        return widget.id, widget.ptr.op

    def query_next(self, widget_id):
        widget = self._widgets[widget_id]
        next = widget.ptr.best_next.ref
        return next

    def query_operation(self, widget_id):
        widget = self._widgets[widget_id]
        return widget.ptr.op

    # TODO this is a user defined function to set the weights of each of the
    # nodes. This will be need to be passed in by the user
    def set_weights(self, cell):
        pass

    def update_statistics(self, time):
        total_widgets = len(self._widgets)
        self._total_widgets_per_time.append([time, total_widgets])

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

        

        


