import argparse
import json
import os
from dataclasses import asdict

from cus_types_main import type_statement
from utils import IDManager


STATEMENT_FOLDER = "contents/statement"
VALID_TYPES = ["assumption", "proposition", "normal"]


def create_statement(
    type: str,
    conclusion: list[str],
    hypothesis: list[str] | None = None
) -> str:
    """Create a new statement and save it to file.

    Args:
        type: Statement type, one of "assumption", "proposition", "normal"
        conclusion: List of conclusion strings
        hypothesis: Optional list of hypothesis strings

    Returns:
        The new statement ID
    """
    if type not in VALID_TYPES:
        raise ValueError(f"Invalid type '{type}'. Expected one of: {VALID_TYPES}")

    id_manager = IDManager()
    statement_id = id_manager.generate_id("s")

    # Use empty list if hypothesis is None
    hypothesis_list = hypothesis if hypothesis is not None else []

    statement = type_statement(
        id=statement_id,
        type=type,
        conclusion=conclusion,
        hypothesis=hypothesis_list
    )

    os.makedirs(STATEMENT_FOLDER, exist_ok=True)

    statement_path = os.path.join(STATEMENT_FOLDER, f"{statement_id}.json")
    with open(statement_path, "w") as f:
        json.dump(asdict(statement), f, indent=4)

    return statement_id


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize a new statement")
    parser.add_argument('--type', type=str, required=True, choices=VALID_TYPES)
    parser.add_argument('--conclusion', nargs='+', type=str, required=True)
    parser.add_argument('--hypothesis', nargs='+', type=str, default=None)

    args = parser.parse_args()

    statement_id = create_statement(
        type=args.type,
        conclusion=args.conclusion,
        hypothesis=args.hypothesis
    )
    print(f"Created statement: {statement_id}")
