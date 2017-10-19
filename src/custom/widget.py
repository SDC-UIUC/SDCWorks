from generic.widget import GenericWidget

class CustomWidget(GenericWidget):
    def __init__(self, req_name):
        super().__init__(req_name)

        # Controller varirables
        self.feasible_ptr = None
