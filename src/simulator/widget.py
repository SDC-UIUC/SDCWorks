from uuid import uuid4

class Widget:
    def __init__(self, requirement):
        self.id = uuid4()
        self.requirement = requirement
        self.cur_req = requirement.root

    def select_next_op(self, req_name):
        selected_next = False
        for next in self.cur_req.get_nexts():
            if next.name == req_name:
                self.cur_req = next
                selected_next = True

        if not selected_next:
            raise ValueError("No requirement with %s found" % req_name)

