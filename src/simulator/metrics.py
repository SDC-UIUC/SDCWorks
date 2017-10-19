from collections import OrderedDict
import matplotlib.pyplot as plt
import numpy as np
import os, pickle

class Metrics:
    def __init__(self, directory, requirements):
        # Create directories
        self._metrics_dir = os.path.join(directory, "metrics")
        if not os.path.exists(self._metrics_dir):
            os.makedirs(self._metrics_dir)

        self._data_dir = os.path.join(self._metrics_dir, "data")
        if not os.path.exists(self._data_dir):
            os.makedirs(self._data_dir)

        self._plots_dir = os.path.join(self._metrics_dir, "plots")
        if not os.path.exists(self._plots_dir):
            os.makedirs(self._plots_dir)

        # Variables
        self._requirements = requirements

        # Constants
        self._ticks_per_hour = 3600.0
        self._font_size = 22
        self._tick_size = 18


        # Metrics
        self._load_data = []
        self._load_sum = 0

        self._throughput_data = OrderedDict()
        self._throughput_totals = OrderedDict()

        self._latency_data = OrderedDict()
        self._latency_sum = OrderedDict()

        for name in list(requirements.keys()):
            self._throughput_data[name] = []
            self._throughput_totals[name] = 0

            self._latency_data[name] = []
            self._latency_sum[name] = 0

    def update_metrics_instantiation(self, widget):
        self._load_sum += 1

    def update_metrics_termination(self, widget):
        req_name = widget.req_name

        self._load_sum -= 1 
        self._throughput_totals[req_name] += 1
        self._latency_sum[req_name] += widget.processing_time

    def update(self, cur_time):
        # Load
        load = [cur_time, self._load_sum]
        self._load_data.append(load)

        # Throughput and latency
        for req_name in list(self._requirements.keys()):
            if cur_time <= 0:
                req_throughput = 0
            else:
                req_throughput = self._throughput_totals[req_name] / cur_time * \
                        self._ticks_per_hour 
            throughput = [cur_time, req_throughput]
            self._throughput_data[req_name].append(throughput)

            req_total = self._throughput_totals[req_name]
            if req_total == 0:
                req_latency = 0
            else:
                req_latency = self._latency_sum[req_name] / req_total
            latency = [cur_time, req_latency]
            self._latency_data[req_name].append(latency)

    def plot_metrics(self):
        # Output plots
        load_plot_path = os.path.join(self._plots_dir, "load.png")
        throughput_plot_path = os.path.join(self._plots_dir, "throughput.png")
        latency_plot_path = os.path.join(self._plots_dir, "latency.png")

        # Plot load
        load_data = np.array(self._load_data)
        time = load_data[:, 0]
        widgets = load_data[:, 1]

        plt.figure(0)
        plt.plot(time, widgets)
        plt.xlabel("Time (s)", fontsize=self._font_size)
        plt.ylabel("# of live widgets", fontsize=self._font_size)
        plt.xticks(fontsize=self._tick_size)
        plt.yticks(fontsize=self._tick_size)
        plt.title("Load vs. time", fontsize=self._font_size)
        plt.savefig(load_plot_path)

        # Plot throughput
        plt.figure(1)
        for req_name, data in self._throughput_data.items():
            data = np.array(data)
            time = data[:, 0]
            throughput = data[:, 1]
            plt.plot(time, throughput, label=req_name)

        plt.xlabel("Time (s)", fontsize=self._font_size)
        plt.ylabel("Throughput (JPH)", fontsize=self._font_size)
        plt.xticks(fontsize=self._tick_size)
        plt.yticks(fontsize=self._tick_size)
        plt.title("Average throughput vs. time", fontsize=self._font_size)
        plt.legend(loc="lower right", fontsize=self._font_size)
        plt.savefig(throughput_plot_path)

        # Plot latency
        plt.figure(2)
        for req_name, data in self._latency_data.items():
            data = np.array(data)
            time = data[:, 0]
            latency = data[:, 1]
            plt.plot(time, latency, label=req_name)

        plt.xlabel("Time (s)", fontsize=self._font_size)
        plt.ylabel("End-to-end delay (s)", fontsize=self._font_size)
        plt.xticks(fontsize=self._tick_size)
        plt.yticks(fontsize=self._tick_size)
        plt.title("Average end-to-end-delay vs. time", fontsize=self._font_size)
        plt.legend(loc="lower right", fontsize=self._font_size)
        plt.savefig(latency_plot_path)

        # Clear plots
        plt.clf()

    def save_metrics_data(self):
        # Save total number of widgets
        out_path = os.path.join(self._data_dir, "load.pickle")
        with open(out_path, 'wb') as out_file:
            pickle.dump(self._load_data, out_file)  

        # Save throughput
        out_path = os.path.join(self._data_dir, "throughput.pickle")
        with open(out_path, 'wb') as out_file:
            pickle.dump(self._throughput_data, out_file)

        # Save latency
        out_path = os.path.join(self._data_dir, "latency.pickle")
        with open(out_path, 'wb') as out_file:
            pickle.dump(self._latency_data, out_file) 
