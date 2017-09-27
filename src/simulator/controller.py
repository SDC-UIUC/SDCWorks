

class Controller():
    def __init__(self, network):
        self._network = network
        self._widgets = {}
        self._control_table = None

        # Initialize network with controller functions
        network.add_dispatch_command("controller", "instantiation",
            self.notify_instantiation)
        network.add_dispatch_command("controller", "enqueue",
            self.notify_enqueue)

    # TODO source_id is not used for now
    def notify_instantiation(self, widget_id, req, source_id):
        req_ptr = self._control_table[req]

        widget = VirtualWidget(widget_id, req, req_ptr)
        self.widgets[widget.id] = widget

class VirtualWidget():
    def __init__(self, id, req, ptr):
        self.id = id
        self.req = req
        self.ptr = ptr
        
        self.op_list = []
