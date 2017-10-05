from uuid import uuid4
    
# FIXME in the future this should only be an id
class RealWidget:
    def __init__(self, id):
        self.id = id

    def __str__(self):
        return "Widget: %s" % (self.id)

class VirtualWidget:
    def __init__(self, req_id):
        self.id = str(uuid4())
        self.req_id = req_id

        self.feasible_ptr = None
        self.completed_ops = []
        self.processing_time = 0

        self.path = []

"""
class Widget:
    def __init__(self, requirement):
        self.id = str(uuid4())
        self.requirement = requirement
        self.cur_req = requirement.root

    def __str__(self):
        str = (
            "Widget: " + self.id + ", "
            "requirement: " + self.requirement.name + ", "
            "current op: " + self.cur_req.ops + "\n"
        )

        return str

    def select_next_op(self, req_name):
        selected_next = False
        for next in self.cur_req.get_nexts():
            if next.name == req_name:
                self.cur_req = next
                selected_next = True

        if not selected_next:
            raise ValueError("No requirement with %s found" % req_name)
"""
