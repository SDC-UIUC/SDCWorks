#from components.conveyancegraph import ConveyanceGraph
#from components.requirements import Requirements
from simulator.conveyancegraph import ConveyanceGraph
from simulator.requirements import Requirements
from subprocess import call
import os, yaml

from generic.graph import *

import pdb

def test_graph_requirements():
    # Paths
    dir = "one-cell"
    dir_path = os.path.join("../examples", dir)
    dir_dot_path = os.path.join(dir_path, "dot")
    dir_png_path = os.path.join(dir_path, "png")

    req_path = os.path.join(dir_path, "requirement.yaml")
    requirements = Requirements(req_path)
    for i, requirement in enumerate(requirements.requirements):
        req_file = "requirement.%s" % (requirement.name)
        req_dot_path = os.path.join(dir_dot_path, req_file + ".dot")
        req_png_path = os.path.join(dir_png_path, req_file + ".png")

        requirement.generate_output_files(req_dot_path, req_png_path)

def test_graph():
    n1 = GraphNode("Source", label="Source")
    n2 = GraphNode("A1", label="A")
    n3 = GraphNode("Sink", label="Sink")

    graph = Graph("One-Cell")

    graph.add_graph_nodes(n1)
    graph.add_graph_nodes([n2, n3])

    graph.add_graph_edges(n1.name, [n2.name])
    graph.add_graph_edges(n2.name, n3.name)

    #graph.generate_output_files("test.dot", "test.png")

def test_examples(idx=None):
    # Constants
    dirs = ["one-cell", "dup-seq", "forked-dup"]
    ground_truth = [
            [True],
            [True, True, True, True, False],
            [True, True, False],
    ]

    if dirs_idx == None:
        test_dirs = dirs
        test_ground_truth = ground_truth
    else:
        test_dirs = list(map(lambda i: dirs[i], idx))
        test_ground_truth = list(map(lambda i: ground_truth[i], idx))

    # Test all examples
    for idx, dir in enumerate(test_dirs):
        check_str = "Checking '%s' plant" % (dir)
        div_str = '*' * len(check_str)
        print(check_str + '\n' + div_str)

        # Paths
        dir_path = os.path.join("../examples", dir)
        dir_dot_path = os.path.join(dir_path, "dot")
        dir_png_path = os.path.join(dir_path, "png")

        graph_path = os.path.join(dir_path, "graph.yaml")
        graph_dot_path = os.path.join(dir_dot_path, "graph.dot")
        graph_png_path = os.path.join(dir_png_path, "graph.png")

        conv_graph = ConveyanceGraph(graph_path)
        conv_graph.generate_output_files(graph_dot_path, graph_png_path)

        #conv_graph.generate_graph_dot(graph_dot_path)
        #call(["dot", graph_dot_path, "-Tpng", "-o" + graph_png_path])

        return

        # Parse and visualize requirements
        req_path = os.path.join(dir_path, "requirement.yaml")
        requirements = Requirements(req_path)
        for i, requirement in enumerate(requirements.requirements):
            req_file = "requirement.%s" % (requirement.name)
            req_dot_path = os.path.join(dir_dot_path, req_file + ".dot")
            requirement.generate_requirment_dot(req_dot_path)

            req_png_path = os.path.join(dir_png_path, req_file + ".png")
            call(["dot", req_dot_path, "-Tpng", "-o" + req_png_path])

        # Check requirements feasibility
        feasibilities, subgraphs = conv_graph.check_requirements_feasibility(requirements.requirements)
        
        # Visualize subgraphs
        for i, subgraph in enumerate(subgraphs):
            subgraph_file = "subgraph.requirement.%d.dot" % (i)
            subgraph_dot_path = os.path.join(dir_dot_path, subgraph_file)
            subgraph.generate_subgraph_dot(subgraph_dot_path)

            subgraph_png_path = os.path.join(dir_png_path, subgraph_file)
            call(["dot", subgraph_dot_path, "-Tpng", "-o" + subgraph_png_path])

        assert test_ground_truth[idx] == feasibilities

def test_cycles():
    dir_path = os.path.join("../examples", "cycles")
    dir_dot_path = os.path.join(dir_path, "dot")
    dir_png_path = os.path.join(dir_path, "png")

    # Graph
    graph_path, graph_dot_path, graph_png_path = get_graph_paths("cycles")
    conv_graph = ConveyanceGraph(graph_path)
    conv_graph.generate_graph_dot(graph_dot_path)
    call(["dot", graph_dot_path, "-Tpng", "-o" + graph_png_path])

    # Requirements
    req_path = os.path.join(dir_path, "requirements.yaml")
    requirements = Requirements(req_path)
    for i, requirement in enumerate(requirements.requirements):
        req_file = "requirement.%s" % (requirement.name)
        req_dot_path = os.path.join(dir_dot_path, req_file + ".dot")
        requirement.generate_requirment_dot(req_dot_path)

        req_png_path = os.path.join(dir_png_path, req_file + ".png")
        call(["dot", req_dot_path, "-Tpng", "-o" + req_png_path])

    feasibilities = conv_graph.check_requirements_feasibility(requirements.requirements)
    print(feasibilities)

def get_graph_paths(dir):
        dir_path = os.path.join("../examples", dir)
        dir_dot_path = os.path.join(dir_path, "dot")
        dir_png_path = os.path.join(dir_path, "png")

        graph_path = os.path.join(dir_path, "graph.yaml")
        graph_dot_path = os.path.join(dir_dot_path, "graph.dot")
        graph_png_path = os.path.join(dir_png_path, "graph.png")

        return graph_path, graph_dot_path, graph_png_path


if "__main__" == __name__:
    #test_graph_requirements()
    #test_graph()

    dirs_idx = [0]
    test_examples(dirs_idx)

    #test_cycles()
