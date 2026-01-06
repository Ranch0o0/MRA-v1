import argparse
from dataclasses import asdict

from cus_types_main import type_statement
from utils import IDManager, commit_objects


STATEMENT_FOLDER = "contents/statement"
VALID_TYPES = ["assumption", "proposition", "normal"]


def create_statement(
    type: str,
    conclusion: list[str],
    hypothesis: list[str] | None = None,
    root_change: bool = True,
    status: str = "pending"
) -> str | tuple[str, dict]:
    """Create a new statement and save it to file.

    Args:
        type: Statement type, one of "assumption", "proposition", "normal"
        conclusion: List of conclusion strings
        hypothesis: Optional list of hypothesis strings
        root_change: If True, commit to file and log; if False, return object for parent to handle
        status: Initial status of the statement (default "pending")

    Returns:
        If root_change=True: The new statement ID
        If root_change=False: Tuple of (object_type, object_data) for parent to commit
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
        hypothesis=hypothesis_list,
        status=status
    )

    statement_data = asdict(statement)

    if root_change:
        # Commit to file and create log entry
        commit_objects([("s", statement_data)])
        return statement_id
    else:
        # Return object for parent to handle
        return ("s", statement_data)


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
