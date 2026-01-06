import argparse
import json
import os
import re
from dataclasses import asdict

from cus_types_main import type_problem
from utils import IDManager, commit_objects, OBJECT_FOLDERS
from state_init import create_statement


STATEMENT_FOLDER = OBJECT_FOLDERS["s"]  # Used by load_statement_conclusion()


def parse_statement_id(text: str) -> str | None:
    """Extract statement ID from text starting with (s-...) or (e-...).

    Args:
        text: Input text to parse

    Returns:
        Statement ID if found, else None
    """
    text = text.lstrip()
    if not text.startswith('('):
        return None

    # Match pattern like (s-001), (s-a001), (e-001), etc.
    match = re.match(r'^\(([se]-[a-z]*\d+)\)', text)
    if match:
        return match.group(1)
    return None


def load_statement_conclusion(statement_id: str) -> str | None:
    """Load conclusion from statement file.

    Args:
        statement_id: Statement ID (e.g., "s-001")

    Returns:
        Conclusion text (joined from list) if file exists, else None
    """
    statement_path = os.path.join(STATEMENT_FOLDER, f"{statement_id}.json")

    if not os.path.exists(statement_path):
        return None

    try:
        with open(statement_path, 'r') as f:
            statement_data = json.load(f)

        conclusion = statement_data.get('conclusion', [])
        if isinstance(conclusion, list):
            return ' '.join(conclusion)
        return str(conclusion)
    except Exception:
        return None


def process_hypothesis_item(item: str, initial: bool) -> tuple[str, list[tuple[str, dict]]]:
    """Process single hypothesis item with smart ID handling.

    Args:
        item: Hypothesis item text
        initial: Whether this is an initial problem

    Returns:
        Tuple of (formatted_hypothesis_string, list of objects to create)
    """
    # Check for existing statement ID
    statement_id = parse_statement_id(item)

    if statement_id:
        # Try to load the statement
        conclusion = load_statement_conclusion(statement_id)
        if conclusion:
            # Existing statement found, no new objects to create
            return (f"({statement_id}) {conclusion}", [])

        # ID format valid but file doesn't exist - strip invalid ID
        # Remove the "(id) " prefix
        cleaned_text = re.sub(r'^\([se]-[a-z]*\d+\)\s*', '', item.lstrip()).strip()
    else:
        # No ID pattern found, use original text
        cleaned_text = item.strip()

    # Create new statement with root_change=False to get object data
    statement_type = "assumption" if initial else "normal"
    # Set status='true' if initial, else 'pending' (born with correct status)
    status = "true" if initial else "pending"

    obj_type, obj_data = create_statement(
        type=statement_type,
        conclusion=[cleaned_text],
        hypothesis=None,
        root_change=False,
        status=status
    )

    return (f"({obj_data['id']}) {cleaned_text}", [(obj_type, obj_data)])


def create_problem(
    hypothesis: list[str],
    objectives: list[str],
    initial: bool = False,
    root_change: bool = True
) -> str | tuple[str, list[tuple[str, dict]]]:
    """Create a new problem and save it to file.

    Args:
        hypothesis: List of hypothesis items
        objectives: List of objective items
        initial: Whether this is an initial problem (statements born with status='true')
        root_change: If True, commit to file and log; if False, return objects for parent to handle

    Returns:
        If root_change=True: The new problem ID
        If root_change=False: Tuple of (problem_id, list of objects to create)
    """
    # Collect all objects to be created
    objects_to_create = []
    processed_hypothesis = []

    # Process each hypothesis item
    for item in hypothesis:
        formatted, new_objects = process_hypothesis_item(item, initial)
        processed_hypothesis.append(formatted)
        objects_to_create.extend(new_objects)

    # Generate problem ID
    id_manager = IDManager()
    problem_id = id_manager.generate_id("p")

    # Create problem with processed hypothesis
    problem = type_problem(
        id=problem_id,
        hypothesis=processed_hypothesis,
        objectives=objectives
    )

    problem_data = asdict(problem)
    objects_to_create.append(("p", problem_data))

    if root_change:
        # Commit all objects and create log
        commit_objects(objects_to_create)
        return problem_id
    else:
        # Return all objects for parent to handle
        return (problem_id, objects_to_create)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize a new problem")
    parser.add_argument('--hypothesis', nargs='+', type=str, required=True)
    parser.add_argument('--objectives', nargs='+', type=str, required=True)
    parser.add_argument('--initial', action='store_true', default=False)

    args = parser.parse_args()

    problem_id = create_problem(args.hypothesis, args.objectives, args.initial)
    print(f"Created problem: {problem_id}")
