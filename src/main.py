from parser.parser import parse_plant, parse_requirements
import os, yaml

def test_examples():
    # Constants
    dirs = ["one-cell", "dup-seq", "forked-dup"]
    ground_truth = [
            [True],
            [True, True, True, True, False],
    ]

    # Test all examples
    for idx, dir in enumerate(dirs):
        check_str = "Checking '%s' plant" % (dir)
        div_str = '*' * len(check_str)
        print(check_str + '\n' + div_str)

        # Paths
        dir_path = os.path.join("../examples", dir)
        plant_path = os.path.join(dir_path, "plant.yaml")
        plant_dot_path = os.path.join(dir_path, "plant.dot")
        req_path = os.path.join(dir_path, "requirement.yaml")

        # Parse and visualize conveyance graphs
        conv_graph = parse_plant(plant_path)    
        conv_graph.generate_graph_dot(plant_dot_path)

        """
        # Parse and visualize requirements
        requirements = parse_requirements(req_path)
        for i, requirement in enumerate(requirements):
            req_dot_file = "requirement.%s.dot" % (requirement.name)
            req_dot_path = os.path.join(dir_path, req_dot_file)
            requirement.generate_requirment_dot(req_dot_path)

        # Check requirements feasibility
        feasibilities = conv_graph.check_requirements_feasibility(requirements)
        assert ground_truth[idx] == feasibilities
        """

if "__main__" == __name__:
    test_examples()
