import argparse
import json
import os
from dataclasses import asdict

from cus_types_main import type_problem
from prob_utils import id_generation


PROBLEM_FOLDER = "contents/problem"


def create_problem(hypothesis: list[str], objectives: list[str]) -> str:
    """Create a new problem and save it to file."""
    problem_id = id_generation("p")

    problem = type_problem(
        id=problem_id,
        hypothesis=hypothesis,
        objectives=objectives
    )

    os.makedirs(PROBLEM_FOLDER, exist_ok=True)

    problem_path = os.path.join(PROBLEM_FOLDER, f"{problem_id}.json")
    with open(problem_path, "w") as f:
        json.dump(asdict(problem), f, indent=4)

    return problem_id


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize a new problem")
    parser.add_argument('--hypothesis', nargs='+', type=str, required=True)
    parser.add_argument('--objectives', nargs='+', type=str, required=True)

    args = parser.parse_args()

    problem_id = create_problem(args.hypothesis, args.objectives)
    print(f"Created problem: {problem_id}")
