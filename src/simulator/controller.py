from simulator.widgets import VirtualWidget

import pdb

class Controller():
    def __init__(self, network, requirements):
        self._network = network
        self.requirements = requirements

        self._control_table = None
        self.requirement_keys = None
        self._widgets = {}

        # Rename this to completed
        self._completed_widgets = {}
        for requirement in self.requirements:
            self._completed_widgets[requirement.id] = {}

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
        for req_id, req_dict in self._completed_widgets.items():

            # FIXME
            req_str = "Requirement name: %s\n" % (req_id)
            for path, widgets in req_dict.items():
                req_str += "\t%s: %d\n" % (str(path), len(widgets))

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

    # FIXME spawns always
    def query_instantiate(self):
        req_id = self.requirement_keys[0]

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

        

        


