"""Create or update problems.

This script handles both problem creation and updates.
- No --id: Create mode (objectives required)
- With --id: Update mode

For initial problem creation from puzzle, use prob_init.py instead.
"""
import argparse
import json
import os
import re
from dataclasses import asdict
from typing import Optional

from cus_types_main import type_problem, type_statement, type_object_change
from utils import IDManager, handle_changes, load_object, OBJECT_FOLDERS


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
    """Process single hypothesis item for problem creation.

    New statements are created with type='normal' and status='pending'.

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

    # Create new statement with type='normal' and status='pending'
    statement = type_statement(
        id=new_statement_id,
        type="normal",
        conclusion=[cleaned_text],
        status="pending"
    )

    change = type_object_change(
        change_type="create",
        obj=statement
    )

    return (f"({new_statement_id}) {cleaned_text}", [change])


def validate_problem_id(obj_id: str) -> bool:
    """Validate problem ID format and check existence.

    Args:
        obj_id: Problem ID to validate (e.g., "p-001")

    Returns:
        True if valid and exists

    Raises:
        ValueError: If ID format is invalid or doesn't exist
    """
    if not obj_id.startswith("p-"):
        raise ValueError(f"Invalid problem ID format: {obj_id}. Expected 'p-XXX' format.")

    # Check if the problem exists by trying to load it
    try:
        load_object(obj_id)
        return True
    except FileNotFoundError:
        raise ValueError(f"Problem {obj_id} does not exist.")


def handle_problem(
    id: Optional[str] = None,
    objectives: Optional[list[str]] = None,
    hypothesis: Optional[list[str]] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    summary: Optional[str] = None,
    preliminaries: Optional[tuple[str, list[str]]] = None,
    progresses: Optional[tuple[str, list[str]]] = None,
    solution_cot: Optional[tuple[str, list[str]]] = None,
    solution_full: Optional[str] = None,
    solution_ref: Optional[tuple[str, list[str]]] = None,
    root_change: bool = True
) -> str | tuple[str, list[type_object_change]]:
    """Handle problem creation or update.

    Args:
        id: Problem ID for update mode; None for create mode
        objectives: List of objectives (required for create mode)
        hypothesis: List of hypothesis items
        status: Problem status
        priority: Problem priority
        summary: Problem summary
        preliminaries: For multiple mode: (mode, values) where mode is 'overwrite' or 'append'
        progresses: Progress items (mode, values)
        solution_cot: Chain-of-thought for solution (mode, values)
        solution_full: Full solution text
        solution_ref: Solution references (mode, values)
        root_change: If True, commit changes; if False, return changes for parent

    Returns:
        If root_change=True: problem_id (for create) or log_id (for update)
        If root_change=False: tuple of (problem_id, list of type_object_change)
    """
    if id is None:
        # CREATE MODE
        return _create_problem(
            objectives=objectives,
            hypothesis=hypothesis,
            status=status,
            priority=priority,
            summary=summary,
            preliminaries=preliminaries,
            progresses=progresses,
            solution_cot=solution_cot,
            solution_full=solution_full,
            solution_ref=solution_ref,
            root_change=root_change
        )
    else:
        # UPDATE MODE
        return _update_problem(
            id=id,
            objectives=objectives,
            hypothesis=hypothesis,
            status=status,
            priority=priority,
            summary=summary,
            preliminaries=preliminaries,
            progresses=progresses,
            solution_cot=solution_cot,
            solution_full=solution_full,
            solution_ref=solution_ref,
            root_change=root_change
        )


def _create_problem(
    objectives: Optional[list[str]],
    hypothesis: Optional[list[str]],
    status: Optional[str],
    priority: Optional[str],
    summary: Optional[str],
    preliminaries: Optional[tuple[str, list[str]]],
    progresses: Optional[tuple[str, list[str]]],
    solution_cot: Optional[tuple[str, list[str]]],
    solution_full: Optional[str],
    solution_ref: Optional[tuple[str, list[str]]],
    root_change: bool
) -> str | tuple[str, list[type_object_change]]:
    """Create a new problem."""
    # Validate required fields
    if objectives is None:
        raise ValueError("'objectives' is required for creating a problem.")

    # Collect all changes
    changes = []
    processed_hypothesis = []

    # Process hypothesis items if provided
    if hypothesis:
        for item in hypothesis:
            formatted, new_changes = process_hypothesis_item(item)
            processed_hypothesis.append(formatted)
            changes.extend(new_changes)

    # Generate problem ID
    id_manager = IDManager()
    problem_id = id_manager.generate_id("p")

    # Build problem object
    problem = type_problem(
        id=problem_id,
        hypothesis=processed_hypothesis,
        objectives=objectives,
        status=status if status is not None else "unresolved",
        priority=priority if priority is not None else "",
        summary=summary if summary is not None else ""
    )

    # Handle list fields
    if preliminaries is not None:
        _, values = preliminaries
        problem.preliminaries = list(values)
    if progresses is not None:
        _, values = progresses
        problem.progresses = list(values)

    # Handle solution fields
    if solution_cot is not None:
        _, values = solution_cot
        problem.solution.cot = list(values)
    if solution_full is not None:
        problem.solution.full = solution_full
    if solution_ref is not None:
        _, values = solution_ref
        problem.solution.ref = list(values)

    # Create change object
    problem_change = type_object_change(
        change_type="create",
        obj=problem
    )
    changes.append(problem_change)

    if root_change:
        handle_changes(changes)
        return problem_id
    else:
        return (problem_id, changes)


def _update_problem(
    id: str,
    objectives: Optional[list[str]],
    hypothesis: Optional[list[str]],
    status: Optional[str],
    priority: Optional[str],
    summary: Optional[str],
    preliminaries: Optional[tuple[str, list[str]]],
    progresses: Optional[tuple[str, list[str]]],
    solution_cot: Optional[tuple[str, list[str]]],
    solution_full: Optional[str],
    solution_ref: Optional[tuple[str, list[str]]],
    root_change: bool
) -> str | tuple[str, list[type_object_change]]:
    """Update an existing problem."""
    # Validate ID
    validate_problem_id(id)

    # Build updates dict
    updates = {}

    if objectives is not None:
        updates["objectives"] = objectives
    if hypothesis is not None:
        updates["hypothesis"] = hypothesis  # Direct overwrite for update mode
    if status is not None:
        updates["status"] = status
    if priority is not None:
        updates["priority"] = priority
    if summary is not None:
        updates["summary"] = summary
    if preliminaries is not None:
        updates["preliminaries"] = preliminaries  # (mode, values) tuple
    if progresses is not None:
        updates["progresses"] = progresses
    if solution_cot is not None:
        updates["solution.cot"] = solution_cot
    if solution_full is not None:
        updates["solution.full"] = solution_full
    if solution_ref is not None:
        updates["solution.ref"] = solution_ref

    if not updates:
        raise ValueError("No updates provided for problem update.")

    # Load existing object to create a placeholder for the change
    existing = load_object(id)

    # Create a minimal problem object for the change (just need the id)
    placeholder = type_problem(
        id=id,
        hypothesis=existing["hypothesis"],
        objectives=existing["objectives"]
    )

    # Create change object
    change = type_object_change(
        change_type="update",
        obj=placeholder,
        updates=updates
    )

    if root_change:
        log_id, _, modified_ids = handle_changes([change])
        return log_id
    else:
        return (id, [change])


def build_args_from_parsed(args) -> dict:
    """Convert parsed args to function kwargs.

    Args:
        args: Parsed argparse namespace

    Returns:
        Dict of kwargs for handle_problem
    """
    kwargs = {}

    kwargs["id"] = args.id

    # Direct fields
    if args.objectives is not None:
        kwargs["objectives"] = args.objectives
    if args.status is not None:
        kwargs["status"] = args.status
    if args.priority is not None:
        kwargs["priority"] = args.priority
    if args.summary is not None:
        kwargs["summary"] = args.summary
    if args.solution_full is not None:
        kwargs["solution_full"] = args.solution_full

    # Hypothesis - can be used directly for create, or as overwrite for update
    if args.hypothesis:
        kwargs["hypothesis"] = args.hypothesis

    # Multiple-value fields (mode + values)
    if args.preliminaries:
        mode = args.preliminaries[0]
        values = args.preliminaries[1:]
        kwargs["preliminaries"] = (mode, values)
    if args.progresses:
        mode = args.progresses[0]
        values = args.progresses[1:]
        kwargs["progresses"] = (mode, values)
    if args.solution_cot:
        mode = args.solution_cot[0]
        values = args.solution_cot[1:]
        kwargs["solution_cot"] = (mode, values)
    if args.solution_ref:
        mode = args.solution_ref[0]
        values = args.solution_ref[1:]
        kwargs["solution_ref"] = (mode, values)

    return kwargs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create or update a problem")

    # Mode identifier
    parser.add_argument('--id', type=str, default=None,
                        help='Problem ID for update mode; omit for create mode')

    # Single-value params
    parser.add_argument('--status', type=str,
                        help='Problem status')
    parser.add_argument('--priority', type=str,
                        help='Problem priority')
    parser.add_argument('--summary', type=str,
                        help='Problem summary')
    parser.add_argument('--solution.full', type=str, dest='solution_full',
                        help='Full solution text')

    # List params (direct for objectives, mode+values for others)
    parser.add_argument('--objectives', nargs='+', type=str,
                        help='Objectives (required for create mode)')
    parser.add_argument('--hypothesis', nargs='+', type=str,
                        help='Hypothesis items')
    parser.add_argument('--preliminaries', nargs='+', type=str,
                        help='Mode (Overwrite/Append) followed by preliminary items')
    parser.add_argument('--progresses', nargs='+', type=str,
                        help='Mode (Overwrite/Append) followed by progress items')
    parser.add_argument('--solution.cot', nargs='+', type=str, dest='solution_cot',
                        help='Mode (Overwrite/Append) followed by chain-of-thought steps')
    parser.add_argument('--solution.ref', nargs='+', type=str, dest='solution_ref',
                        help='Mode (Overwrite/Append) followed by references')

    args = parser.parse_args()

    kwargs = build_args_from_parsed(args)

    # Validate for create mode
    if args.id is None:
        if args.objectives is None:
            parser.error("--objectives is required for create mode (when --id is not provided)")

    result = handle_problem(**kwargs)

    if args.id is None:
        print(f"Created problem: {result}")
    else:
        print(f"Updated problem {args.id} (log: {result})")
