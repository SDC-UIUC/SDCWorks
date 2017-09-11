from components.cell import Cell
from components.conveyor import Conveyor
import yaml

import pdb

DEBUG = False

# TODO comment me
def parse_graph(graph_yaml):
    # Read and parse YAML
    try:
        with open(graph_yaml, 'r') as graph_file:
            graph_info = graph_file.read()
    except:
        raise EnvironmentError("Unable to open %s" % (graph_yaml))

    graph_data = yaml.load(graph_info)

    # Parse cells
    if "cells" not in graph_data:
        raise ValueError("No key 'cells'")

    cells_dict = graph_data["cells"]
    if cells_dict == None:
        raise ValueError("Key 'cells' is empty")

    cells = []
    for cell_dict in cells_dict:
        cell = _parse_cell(cell_dict["cell"])
        cells.append(cell)

    # Parse conveyors
    if "conveyors" not in graph_data:
        raise ValueError("No key 'conveyors'")
    
    convs_dict = graph_data["conveyors"]
    if convs_dict == None:
        raise ValueError("Key 'conveyors' is empty")

    convs = []
    for conv_dict in convs_dict:
        conv = _parse_conveyor(conv_dict["conveyor"])
        convs.append(conv)

    return cells, convs

       
def _parse_conveyor(conv_dict):
    # Check keys
    keys = ["length", "input", "output"]
    for key in keys:
        if key not in conv_dict:
            raise ValueError("No key '%s' in '%s'" % (key, conv_dict))

    # Connection
    length = conv_dict["length"]
    input = conv_dict["input"]
    output = conv_dict["output"]

    return Conveyor(input, output, length)

def _parse_cell(cell_dict):
    # Check subset of keys
    keys = ["type", "name"]
    for key in keys:
        if key not in cell_dict:
            raise ValueError("No key '%s' in %s" % (key, cell_dict))

    type = cell_dict["type"]
    name = cell_dict["name"]

    # Cell
    ops = {}
    if "operations"  in cell_dict:
        for op in cell_dict["operations"]:
            op_name = op[0]
            op_dur = op[1]
            ops[op_name] = op_dur

    return Cell(type, name, ops)

def parse_requirements(req_yaml):
    # Read and parse YAML
    try:
        with open(req_yaml, 'r') as req_file:
            req_info = req_file.read()
    except:
        raise EnvironmentError("Unable to open %s" % (req_yaml))

    req_data = yaml.load(req_info)

    # Parse requirements
    if "requirements" not in req_data:
        raise ValueError("No key 'requirements'")

    reqs_dict = req_data["requirements"]
    if  reqs_dict == None:
        raise ValueError("Key 'requirements' is empty")

    requirements = []
    for req_dict in reqs_dict:
        requirement = _parse_requirement(req_dict["requirement"])
        requirements.append(requirement)

    return requirements


def _parse_requirement(req_dict):
    # Check keys
    keys = ["name", "nodes", "root", "edges"]
    for key in keys:
        if key not in req_dict:
            raise ValueError("No key '%s' in '%s'" % (key, req_dict))
    
    name = req_dict["name"]
    nodes = req_dict["nodes"]
    root = req_dict["root"]
    edges = req_dict["edges"]
    
    return name, nodes, root, edges

