import argparse
import json
import os
from dataclasses import asdict

from cus_types_main import type_problem


CONFIG_PATH = "contents/config.json"
PROBLEM_FOLDER = "contents/problem"


def ensure_config() -> dict:
    """Ensure config file exists and return its contents."""
    os.makedirs("contents", exist_ok=True)

    if not os.path.exists(CONFIG_PATH):
        config = {
            "count_problems": 0,
            "count_statements": 0,
            "count_experiences": 0
        }
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=4)
    else:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)

    return config


def generate_problem_id() -> str:
    """Generate the next problem ID and update config."""
    config = ensure_config()

    new_count = config["count_problems"] + 1
    problem_id = f"p-{new_count:03d}"

    config["count_problems"] = new_count
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)

    return problem_id


def create_problem(hypothesis: list[str], objectives: list[str]) -> str:
    """Create a new problem and save it to file."""
    problem_id = generate_problem_id()

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
