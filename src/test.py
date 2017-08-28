from parser.parser import parse_plant, parse_requirements
from subprocess import call
import os, yaml

def test_examples():
    # Constants
    dirs = ["one-cell", "dup-seq", "forked-dup"]
    ground_truth = [
            [True],
            [True, True, True, True, False],
            [True, False],
    ]

    # Test all examples
    for idx, dir in enumerate(dirs):
        check_str = "Checking '%s' plant" % (dir)
        div_str = '*' * len(check_str)
        print(check_str + '\n' + div_str)

        # Paths
        dir_path = os.path.join("../examples", dir)
        dir_dot_path = os.path.join(dir_path, "dot")
        dir_png_path = os.path.join(dir_path, "png")

        plant_path = os.path.join(dir_path, "plant.yaml")
        plant_dot_path = os.path.join(dir_dot_path, "plant.dot")
        plant_png_path = os.path.join(dir_png_path, "plant.png")

        conv_graph = parse_plant(plant_path)    
        conv_graph.generate_graph_dot(plant_dot_path)

        call(["dot", plant_dot_path, "-Tpng", "-o" + plant_png_path])

        # Parse and visualize requirements
        req_path = os.path.join(dir_path, "requirement.yaml")
        requirements = parse_requirements(req_path)
        for i, requirement in enumerate(requirements):
            req_file = "requirement.%s" % (requirement.name)
            req_dot_path = os.path.join(dir_dot_path, req_file + ".dot")
            requirement.generate_requirment_dot(req_dot_path)

            req_png_path = os.path.join(dir_png_path, req_file + ".png")
            call(["dot", req_dot_path, "-Tpng", "-o" + req_png_path])

        # Check requirements feasibility
        feasibilities = conv_graph.check_requirements_feasibility(requirements)
        assert ground_truth[idx] == feasibilities

if "__main__" == __name__:
    test_examples()
