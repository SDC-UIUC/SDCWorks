import yaml

# TODO comment me
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

    cells = {
            "source": [],
            "cell": [],
            "sink": []
    }

    for cell_dict in cells_dict:
        if "source" in cell_dict:
            source = _parse_source(cell_dict["source"])
            cells["source"].append(source)
        elif "cell" in cell_dict:
            cell = _parse_cell(cell_dict["cell"])
            cells["cell"].append(cell)
        else:
            sink = _parse_sink(cell_dict["sink"])
            cells["sink"].append(sink)

    # Parse conveyors
    if "conveyors" not in plant_data:
        raise ValueError("No key 'conveyors'")
    
    convs_dict = plant_data["conveyors"]
    if convs_dict == None:
        raise ValueError("Key 'conveyors' is empty")

    convs = []
    for conv_dict in convs_dict:
        conv = _parse_conveyor(conv_dict["conveyor"])
        convs.append(conv)

    return cells, convs

def _parse_cell(cell_dict):
    # Check subset of keys
    keys = ["name", "operations"]
    if any(key not in cell_dict for key in keys):
        raise KeyError("No key '%s' in %s" % (key, cell_dict))

    name = cell_dict["name"]

    # Cell
    ops = {}
    if "operations" in cell_dict:
        for op in cell_dict["operations"]:
            op_name = op[0]
            op_dur = op[1]
            ops[op_name] = op_dur

    cell_attrs = {
        "name": name,
        "ops":  ops,
    }

    return cell_attrs

def _parse_source(source_dict):
    """
    keys = ["name", "spawn_time_type", "spawn_req_type"]
    for key in keys:
        if key not in source_dict:
            raise KeyError("No key '%s' in %s" % (key, source_dict))
    
    spawn_attrs = { 
        "spawn_time_type": source_dict["spawn_time_type"],
        "spawn_req_type": source_dict["spawn_req_type"],
    }

    if spawn_attrs["spawn_time_type"] == "constant":
        spawn_attrs["spawn_time_interval"] = source_dict["spawn_time_interval"]

    if spawn_attrs["spawn_req_type"] == "round-robn":
        spawn_attrs["req_idx"] = 0

    source_attrs = {
        "name": source_dict["name"],
        "spawn_attrs": spawn_attrs,
        "ops": { "INSTANTIATE": 0 }
    }
    """

    keys = ["name"]
    for key in keys:
        if key not in source_dict:
            raise KeyError("No key '%s' in %s" % (key, source_dict))

    source_dict["ops"] = { "INSTANTIATE": 0 }
    return source_dict

def _parse_sink(sink_dict):
    keys = ["name"]
    for key in keys:
        if key not in sink_dict:
            raise KeyError("No key '%s' in %s" % (key, sink_dict))

    sink_dict["ops"] = { "TERMINATE": 0 }
    return sink_dict
       
def _parse_conveyor(conv_dict):
    # Check keys
    keys = ["length", "prev", "next"]
    for key in keys:
        if key not in conv_dict:
            raise ValueError("No key '%s' in '%s'" % (key, conv_dict))

    return conv_dict

# FIXME return source info as well
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

    return req_dict

