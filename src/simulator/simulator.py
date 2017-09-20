from simulator.plant import Plant
from simulator.requirements import Requirements
import os

class Simulator:
    def __init__(self, plant, requirements, algorithm, 
                 directory, delta_time=0.1, end_time=100):
        self.plant = plant
        self.requirements = requirements
        self.algorithm = algorithm

        # Create directories
        self.dot_dir = os.path.join(directory, "dot")
        if not os.path.exists(self.dot_dir):
            os.makedirs(dot_dir)

        self.png_dir = os.path.join(directory, "png")
        if not os.path.exists(self.png_dir):
            os.makedirs(png_dir)

        self.log_dir = os.path.join(directory, "log")
        if not os.path.exists(self.log_dir):
            os.makedirs(log_dir)

        # Plant output
        plant_dot_path = os.path.join(self.dot_dir, "plant.dot")
        plant_png_path = os.path.join(self.png_dir, "plant.png")
        self.plant.generate_output_files(plant_dot_path, plant_png_path)

        # Requirement output
        for requirement in self.requirements:
            req_file = "requirement-%s" % (requirement.name)
            req_dot_path = os.path.join(self.dot_dir, req_file + ".dot")
            req_png_path = os.path.join(self.png_dir, req_file + ".png")
            requirement.generate_output_files(req_dot_path, req_png_path)

        self.start_time = 0
        self.delta_time = delta_time
        self.end_time = end_time

        """
        for source in self.plant.cell
            source.set_requirements(self.requirements)
        """

    def simulate(self):
        print("Starting simulation")

        while (self.start_time <= end_time):
            self.plant.update(delta_time)
            self.start_time += delta_time

        print("Ending simulation")

