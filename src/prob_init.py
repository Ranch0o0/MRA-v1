import argparse
import json
import os
import re
from dataclasses import asdict

from cus_types_main import type_problem
from prob_utils import id_generation
from state_init import create_statement


PROBLEM_FOLDER = "contents/problem"
STATEMENT_FOLDER = "contents/statement"


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


def process_hypothesis_item(item: str, initial: bool) -> str:
    """Process single hypothesis item with smart ID handling.

    Args:
        item: Hypothesis item text
        initial: Whether this is an initial problem

    Returns:
        Formatted hypothesis string with ID
    """
    # Check for existing statement ID
    statement_id = parse_statement_id(item)

    if statement_id:
        # Try to load the statement
        conclusion = load_statement_conclusion(statement_id)
        if conclusion:
            return f"({statement_id}) {conclusion}"

        # ID format valid but file doesn't exist - strip invalid ID
        # Remove the "(id) " prefix
        cleaned_text = re.sub(r'^\([se]-[a-z]*\d+\)\s*', '', item.lstrip()).strip()
    else:
        # No ID pattern found, use original text
        cleaned_text = item.strip()

    # Create new statement
    statement_type = "assumption" if initial else "normal"
    new_statement_id = create_statement(
        type=statement_type,
        conclusion=[cleaned_text],
        hypothesis=None
    )

    return f"({new_statement_id}) {cleaned_text}"


def set_statement_status_true(statement_ids: list[str]):
    """Mark statements as true.

    Args:
        statement_ids: List of statement IDs to update
    """
    for statement_id in statement_ids:
        statement_path = os.path.join(STATEMENT_FOLDER, f"{statement_id}.json")

        if not os.path.exists(statement_path):
            continue

        try:
            with open(statement_path, 'r') as f:
                statement_data = json.load(f)

            statement_data['status'] = 'true'

            with open(statement_path, 'w') as f:
                json.dump(statement_data, f, indent=4)
        except Exception as e:
            print(f"Warning: Could not update status for {statement_id}: {e}")


def create_problem(hypothesis: list[str], objectives: list[str], initial: bool = False) -> str:
    """Create a new problem and save it to file.

    Args:
        hypothesis: List of hypothesis items
        objectives: List of objective items
        initial: Whether this is an initial problem (auto-creates statements)

    Returns:
        The new problem ID
    """
    processed_hypothesis = []
    created_statement_ids = []

    # Process each hypothesis item
    for item in hypothesis:
        processed_item = process_hypothesis_item(item, initial)
        processed_hypothesis.append(processed_item)

        # Extract ID from processed item for status update
        id_match = re.match(r'^\(([se]-[a-z]*\d+)\)', processed_item)
        if id_match:
            created_statement_ids.append(id_match.group(1))

    # Generate problem ID
    problem_id = id_generation("p")

    # Create problem with processed hypothesis
    problem = type_problem(
        id=problem_id,
        hypothesis=processed_hypothesis,
        objectives=objectives
    )

    os.makedirs(PROBLEM_FOLDER, exist_ok=True)

    problem_path = os.path.join(PROBLEM_FOLDER, f"{problem_id}.json")
    with open(problem_path, "w") as f:
        json.dump(asdict(problem), f, indent=4)

    # If initial, mark all statements as true
    if initial:
        set_statement_status_true(created_statement_ids)

    return problem_id


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize a new problem")
    parser.add_argument('--hypothesis', nargs='+', type=str, required=True)
    parser.add_argument('--objectives', nargs='+', type=str, required=True)
    parser.add_argument('--initial', action='store_true', default=False)

    args = parser.parse_args()

    problem_id = create_problem(args.hypothesis, args.objectives, args.initial)
    print(f"Created problem: {problem_id}")
