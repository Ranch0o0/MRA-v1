"""Initialize problem from puzzle.

This script is only used for the initial problem creation from a puzzle.
All hypothesis items are treated as assumptions with status='true'.

For creating subsequent problems or updating problems, use prob.py instead.
"""
import argparse
import json
import os
import re
from dataclasses import asdict

from cus_types_main import type_problem, type_statement, type_object_change
from utils import IDManager, handle_changes, OBJECT_FOLDERS


STATEMENT_FOLDER = OBJECT_FOLDERS["s"]


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


def process_hypothesis_item(item: str) -> tuple[str, list[type_object_change]]:
    """Process single hypothesis item for initial problem.

    All new statements are created as assumptions with status='true'.

    Args:
        item: Hypothesis item text

    Returns:
        Tuple of (formatted_hypothesis_string, list of type_object_change)
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
        cleaned_text = re.sub(r'^\([se]-[a-z]*\d+\)\s*', '', item.lstrip()).strip()
    else:
        # No ID pattern found, use original text
        cleaned_text = item.strip()

    # Generate new statement ID
    id_manager = IDManager()
    new_statement_id = id_manager.generate_id("s")

    # Create new statement as assumption with status='true'
    statement = type_statement(
        id=new_statement_id,
        type="assumption",
        conclusion=[cleaned_text],
        status="true"
    )

    change = type_object_change(
        change_type="create",
        obj=statement
    )

    return (f"({new_statement_id}) {cleaned_text}", [change])


def create_initial_problem(
    hypothesis: list[str],
    objectives: list[str],
    root_change: bool = True
) -> tuple[str, int] | tuple[str, list[type_object_change]]:
    """Create the initial problem from a puzzle.

    This is the entry point for puzzle initialization.
    All hypothesis items are treated as assumptions (status='true').

    Args:
        hypothesis: List of hypothesis items
        objectives: List of objective items
        root_change: If True, commit to file and log; if False, return objects for parent

    Returns:
        If root_change=True: Tuple of (problem_id, nested_statement_count)
        If root_change=False: Tuple of (problem_id, list of type_object_change)
    """
    # Collect all changes to be made
    changes = []
    processed_hypothesis = []
    nested_count = 0

    # Process each hypothesis item
    for item in hypothesis:
        formatted, new_changes = process_hypothesis_item(item)
        processed_hypothesis.append(formatted)
        changes.extend(new_changes)
        nested_count += len(new_changes)

    # Generate problem ID
    id_manager = IDManager()
    problem_id = id_manager.generate_id("p")

    # Create problem with processed hypothesis
    problem = type_problem(
        id=problem_id,
        hypothesis=processed_hypothesis,
        objectives=objectives
    )

    problem_change = type_object_change(
        change_type="create",
        obj=problem
    )
    changes.append(problem_change)

    if root_change:
        # Commit all changes
        handle_changes(changes)
        return (problem_id, nested_count)
    else:
        return (problem_id, changes)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize problem from puzzle")
    parser.add_argument('--hypothesis', nargs='+', type=str, required=True,
                        help='List of hypothesis items')
    parser.add_argument('--objectives', nargs='+', type=str, required=True,
                        help='List of objective items')

    args = parser.parse_args()

    problem_id, nested_count = create_initial_problem(args.hypothesis, args.objectives)

    if nested_count > 0:
        print(f"Created initial problem: {problem_id} [+{nested_count} statements]")
    else:
        print(f"Created initial problem: {problem_id}")
