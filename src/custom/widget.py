from generic.widget import GenericWidget

class Widget(GenericWidget):
    def __init__(self, req_name):
        super().__init__(req_name)

        # Controller varirables
        self.feasible_ptr = None
        self.completed_ops = []
        self.processing_time = 0
        self.plant_path = []
