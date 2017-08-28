# Consider combining all the components intno a single class

from components.cell import Cell
from components.connection import Connection
from components.conveyancegraph import ConveyanceGraph
from components.requirement import Requirement
import yaml

import pdb

DEBUG = False

def parse_plant(plant_yaml):
    # Read and parse YAML
    try:
        with open(plant_yaml, 'r') as plant_file:
            plant_info = plant_file.read()
    except:
        raise EnvironmentError("Unable to open %s" % (plant_yaml))

    plant_data = yaml.load(plant_info)

    # Parse cells
    if "cells" not in plant_data:
        raise ValueError("No key 'cells'")

    cells_dict = plant_data["cells"]
    if cells_dict == None:
        raise ValueError("Key 'cells' is empty")

    cells = {}
    for cell_dict in cells_dict:
        name, cell = _parse_cell(cell_dict["cell"])
        if name in cells:
            raise ValueError("Duplicate name: %s" % (name))
        cells[name] = cell
        
   # Parse connections
    if "connections" not in plant_data:
        raise ValueError("No key 'connections'")

    conns_dict = plant_data["connections"]
    if conns_dict == None:
        raise ValueError("Key 'connections' is empty")
    
    conns = {}
    for conn_dict in conns_dict:
        endpoints, conn = _parse_connection(conn_dict["connection"])
        for endpoint in endpoints:
            if endpoint in conns:
                conns[endpoint].append(conn)
            else:
                conns[endpoint] = [conn]

    # Return conveyance graph
    return ConveyanceGraph(cells, conns)
       
def _parse_connection(conn_dict):
    # Check keys
    keys = ["length", "endpoints"]
    for key in keys:
        if key not in conn_dict:
            raise ValueError("No key '%s' in '%s'" % (key, conn_dict))

    # Connection
    length = conn_dict["length"]
    endpoints = conn_dict["endpoints"]

    return endpoints, Connection(length)

def _parse_cell(cell_dict):
    # Check subset of keys
    keys = ["type", "name"]
    for key in keys:
        if key not in cell_dict:
            raise ValueError("No key '%s' in %s" % (key, cell_dict))

    type = cell_dict["type"]
    name = cell_dict["name"]

    # Cell
    if "operations" not in cell_dict:
        raise ValueError("No key 'operations' in %s" % (cell_dict))

    ops = {}
    for op in cell_dict["operations"]:
        op_name = op[0]
        op_dur = op[1]
        ops[op_name] = op_dur

    return name, Cell(type, name, ops)

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
    
    return Requirement(name, nodes, root, edges)

