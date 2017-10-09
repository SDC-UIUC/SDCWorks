import matplotlib.pyplot as plt
import numpy as np
import os, pickle

import pdb

ONE_CELL = "../../examples/one-cell"
BRANCH = "../../examples/single-branch"
BRANCH_MULT = "../../examples/single-branch-add-one"

FONT_SIZE = 22
TICKS_SIZE = 18

def plot_data(dir):
    # Directories and files
    data_dir = os.path.join(dir, "data")
    plot_dir = os.path.join(dir, "plot")

    # Inputs
    total_widgets_path = os.path.join(data_dir, "total_widgets.pickle")
    throughput_path = os.path.join(data_dir, "throughput.pickle")
    end_to_end_path = os.path.join(data_dir, "end-to-end.pickle")

    # Outputs
    total_widgets_plot = os.path.join(plot_dir, "total_widgets.png")
    throughput_plot = os.path.join(plot_dir, "throughput.png")
    end_to_end_plot = os.path.join(plot_dir, "end-to-end.png")

    # Plot total widgets
    with open(total_widgets_path, 'rb') as file:
        total_widgets = pickle.load(file)

    total_widgets = np.array(total_widgets)
    time = total_widgets[:, 0]
    widgets = total_widgets[:, 1]

    plt.figure(0)
    plt.plot(time, widgets)
    plt.xlabel("Time (s)", fontsize=FONT_SIZE)
    plt.ylabel("# of live widgets", fontsize=FONT_SIZE)
    plt.xticks(fontsize=TICKS_SIZE)
    plt.yticks(fontsize=TICKS_SIZE)
    plt.title("Live widgets vs. time", fontsize=FONT_SIZE)
    plt.savefig(total_widgets_plot)
    plt.clf()

    # Plot throughput data
    with open(throughput_path, 'rb') as file:
        throughput = pickle.load(file)

    plt.figure(1)
    for req_name, req_data in throughput.items():
        req_data = np.array(req_data)
        time = req_data[:, 0]
        tp = req_data[:, 1]
        plt.plot(time, tp, label=req_name)
    plt.xlabel("Time (s)", fontsize=FONT_SIZE)
    plt.ylabel("Throughput (JPH)", fontsize=FONT_SIZE)
    plt.xticks(fontsize=TICKS_SIZE)
    plt.yticks(fontsize=TICKS_SIZE)
    plt.title("Average throughput vs. time", fontsize=FONT_SIZE)
    plt.legend(loc="lower right", fontsize=FONT_SIZE)
    plt.savefig(throughput_plot)
    plt.clf()

    # Plot end-to-end
    with open(end_to_end_path, 'rb') as file:
        end_to_end = pickle.load(file)

    plt.figure(2)
    for req_name, req_data in end_to_end.items():
        req_data = np.array(req_data)
        time = req_data[:, 0]
        ete = req_data[:, 1]
        plt.plot(time, ete, label=req_name)
    plt.xlabel("Time (s)", fontsize=FONT_SIZE)
    plt.ylabel("End-to-end delay (s)", fontsize=FONT_SIZE)
    plt.xticks(fontsize=TICKS_SIZE)
    plt.yticks(fontsize=TICKS_SIZE)
    plt.title("Average end-to-end-delay vs. time", fontsize=FONT_SIZE)
    plt.legend(loc="lower right", fontsize=FONT_SIZE)
    plt.savefig(end_to_end_plot)
    plt.clf()

    # Clear plots


if "__main__" == __name__:
    plot_data(BRANCH)
    plot_data(BRANCH_MULT)
