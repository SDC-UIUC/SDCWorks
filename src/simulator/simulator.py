from copy import copy
from datetime import datetime

import os, sys

import pdb

class Simulator:
    def __init__(self, plant, controller, requirements, metrics, directory):
        self.controller = controller
        self.plant = plant
        self.requirements = requirements
        self.metrics = metrics

        # Create directories
        self.dot_dir = os.path.join(directory, "dot")
        if not os.path.exists(self.dot_dir):
            os.makedirs(self.dot_dir)

        self.graph_dir = os.path.join(directory, "graph")
        if not os.path.exists(self.graph_dir):
            os.makedirs(self.graph_dir)

        self.log_dir = os.path.join(directory, "log")
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        # Plant output
        plant_dot_path = os.path.join(self.dot_dir, "plant.dot")
        plant_png_path = os.path.join(self.graph_dir, "plant.png")
        self.plant.generate_output_files(plant_dot_path, plant_png_path)

        # Requirement output
        for _, requirement in requirements.items():
            req_file = "requirement-%s" % (requirement.name)
            req_dot_path = os.path.join(self.dot_dir, req_file + ".dot")
            req_png_path = os.path.join(self.graph_dir, req_file + ".png")
            requirement.generate_output_files(req_dot_path, req_png_path)

        # Controller output
        self.controller.generate_output_files(self.dot_dir, self.graph_dir)
    
    def simulate(self, end_time, delta_time):
        print("Starting simulation")

        log_file = "log_" + datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        log_path = os.path.join(self.log_dir, log_file)

        time = -delta_time
        while (time < end_time):
            time += delta_time

            # Updates
            self.controller.update(time)
            self.plant.update(time)
            self.metrics.update(time)

            # Log and write to file
            log_str = self.plant.log() 
            log_str = "Time: %f\n##########\n" % (time) + log_str + "##########\n\n"
            with open(log_path, 'a') as log_file:
                log_file.write(log_str)

        # Log controller statistics
        log_str = self.controller.log_statistics()
        with open(log_path, 'a') as log_file:
            log_file.write(log_str)

        # Save and plot metrics data
        self.metrics.save_metrics_data()
        self.metrics.plot_metrics()  

        print("Ending simulation")


