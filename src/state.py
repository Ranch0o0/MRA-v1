import argparse
from dataclasses import asdict
from typing import Optional

from cus_types_main import type_statement, type_object_change
from utils import IDManager, handle_changes, load_object


VALID_TYPES = ["assumption", "proposition", "normal"]


def validate_statement_id(obj_id: str) -> bool:
    """Validate statement ID format and check existence.

    Args:
        obj_id: Statement ID to validate (e.g., "s-001")

    Returns:
        True if valid and exists

    Raises:
        ValueError: If ID format is invalid or doesn't exist
    """
    if not obj_id.startswith("s-"):
        raise ValueError(f"Invalid statement ID format: {obj_id}. Expected 's-XXX' format.")

    # Check if the statement exists by trying to load it
    try:
        load_object(obj_id)
        return True
    except FileNotFoundError:
        raise ValueError(f"Statement {obj_id} does not exist.")


def handle_statement(
    id: Optional[str] = None,
    type: Optional[str] = None,
    conclusion: Optional[list[str]] = None,
    status: Optional[str] = None,
    reliability: Optional[float] = None,
    hypothesis: Optional[tuple[str, list[str]]] = None,
    proof_cot: Optional[tuple[str, list[str]]] = None,
    proof_full: Optional[str] = None,
    proof_ref: Optional[tuple[str, list[str]]] = None,
    preliminaries: Optional[tuple[str, list[str]]] = None,
    progresses: Optional[tuple[str, list[str]]] = None,
    validation_issues: Optional[tuple[str, list[str]]] = None,
    validation_responses: Optional[tuple[str, list[str]]] = None,
    root_change: bool = True
) -> str | tuple[str, list[type_object_change]]:
    """Handle statement creation or update.

    Args:
        id: Statement ID for update mode; None for create mode
        type: Statement type (required for create mode), one of "assumption", "proposition", "normal"
        conclusion: Conclusion list (required for create mode)
        status: Statement status
        reliability: Reliability score (0.0 to 1.0)
        hypothesis: For multiple mode: (mode, values) where mode is 'overwrite' or 'append'
        proof_cot: Chain-of-thought for proof (mode, values)
        proof_full: Full proof text
        proof_ref: Proof references (mode, values)
        preliminaries: Preliminary statement IDs (mode, values)
        progresses: Progress items (mode, values)
        validation_issues: Validation issues (mode, values)
        validation_responses: Validation responses (mode, values)
        root_change: If True, commit changes; if False, return changes for parent

    Returns:
        If root_change=True: statement_id (for create) or log_id (for update)
        If root_change=False: tuple of (statement_id, list of type_object_change)
    """
    if id is None:
        # CREATE MODE
        return _create_statement(
            type=type,
            conclusion=conclusion,
            status=status,
            reliability=reliability,
            hypothesis=hypothesis,
            proof_cot=proof_cot,
            proof_full=proof_full,
            proof_ref=proof_ref,
            preliminaries=preliminaries,
            progresses=progresses,
            validation_issues=validation_issues,
            validation_responses=validation_responses,
            root_change=root_change
        )
    else:
        # UPDATE MODE
        return _update_statement(
            id=id,
            type=type,
            conclusion=conclusion,
            status=status,
            reliability=reliability,
            hypothesis=hypothesis,
            proof_cot=proof_cot,
            proof_full=proof_full,
            proof_ref=proof_ref,
            preliminaries=preliminaries,
            progresses=progresses,
            validation_issues=validation_issues,
            validation_responses=validation_responses,
            root_change=root_change
        )


def _create_statement(
    type: Optional[str],
    conclusion: Optional[list[str]],
    status: Optional[str],
    reliability: Optional[float],
    hypothesis: Optional[tuple[str, list[str]]],
    proof_cot: Optional[tuple[str, list[str]]],
    proof_full: Optional[str],
    proof_ref: Optional[tuple[str, list[str]]],
    preliminaries: Optional[tuple[str, list[str]]],
    progresses: Optional[tuple[str, list[str]]],
    validation_issues: Optional[tuple[str, list[str]]],
    validation_responses: Optional[tuple[str, list[str]]],
    root_change: bool
) -> str | tuple[str, list[type_object_change]]:
    """Create a new statement."""
    # Validate required fields
    if type is None:
        raise ValueError("'type' is required for creating a statement.")
    if type not in VALID_TYPES:
        raise ValueError(f"Invalid type '{type}'. Expected one of: {VALID_TYPES}")
    if conclusion is None:
        raise ValueError("'conclusion' is required for creating a statement.")

    # Generate new statement ID
    id_manager = IDManager()
    statement_id = id_manager.generate_id("s")

    # Build statement object
    statement = type_statement(
        id=statement_id,
        type=type,
        conclusion=conclusion,
        status=status if status is not None else "pending",
        reliability=reliability if reliability is not None else 0.0
    )

    # Handle hypothesis if provided (extract values from mode tuple)
    if hypothesis is not None:
        _, values = hypothesis
        statement.hypothesis = list(values)

    # Handle proof fields
    if proof_cot is not None:
        _, values = proof_cot
        statement.proof.cot = list(values)
    if proof_full is not None:
        statement.proof.full = proof_full
    if proof_ref is not None:
        _, values = proof_ref
        statement.proof.ref = list(values)

    # Handle preliminaries if provided
    if preliminaries is not None:
        _, values = preliminaries
        statement.preliminaries = list(values)

    # Handle progresses if provided
    if progresses is not None:
        _, values = progresses
        statement.progresses = list(values)

    # Handle validation fields if provided
    if validation_issues is not None:
        _, values = validation_issues
        statement.validation.issues = list(values)
    if validation_responses is not None:
        _, values = validation_responses
        statement.validation.responses = list(values)

    # Create change object
    change = type_object_change(
        change_type="create",
        obj=statement
    )

    if root_change:
        log_id, created_ids, _ = handle_changes([change])
        return statement_id
    else:
        return (statement_id, [change])


def _format_update_fields(updates: dict) -> str:
    """Format update field names for output.

    Groups nested fields (e.g., proof.cot, proof.full -> proof).
    Shows up to 4 fields, then ... if more.

    Args:
        updates: Dict of field paths to values

    Returns:
        Formatted string like "[status,reliability,proof]"
    """
    # Extract unique top-level field names
    fields = set()
    for key in updates.keys():
        # Get top-level field (before first dot)
        top_level = key.split(".")[0]
        fields.add(top_level)

    # Sort for consistent output
    field_list = sorted(fields)

    # Limit to 4 fields
    if len(field_list) > 4:
        return "[" + ",".join(field_list[:4]) + ",...]"
    else:
        return "[" + ",".join(field_list) + "]"


def _update_statement(
    id: str,
    type: Optional[str],
    conclusion: Optional[list[str]],
    status: Optional[str],
    reliability: Optional[float],
    hypothesis: Optional[tuple[str, list[str]]],
    proof_cot: Optional[tuple[str, list[str]]],
    proof_full: Optional[str],
    proof_ref: Optional[tuple[str, list[str]]],
    preliminaries: Optional[tuple[str, list[str]]],
    progresses: Optional[tuple[str, list[str]]],
    validation_issues: Optional[tuple[str, list[str]]],
    validation_responses: Optional[tuple[str, list[str]]],
    root_change: bool
) -> tuple[str, str] | tuple[str, list[type_object_change]]:
    """Update an existing statement.

    Returns:
        If root_change=True: Tuple of (log_id, formatted_fields_string)
        If root_change=False: Tuple of (id, list of type_object_change)
    """
    # Validate ID
    validate_statement_id(id)

    # Build updates dict
    updates = {}

    if type is not None:
        if type not in VALID_TYPES:
            raise ValueError(f"Invalid type '{type}'. Expected one of: {VALID_TYPES}")
        updates["type"] = type
    if conclusion is not None:
        updates["conclusion"] = conclusion
    if status is not None:
        updates["status"] = status
    if reliability is not None:
        updates["reliability"] = reliability
    if hypothesis is not None:
        updates["hypothesis"] = hypothesis  # (mode, values) tuple
    if proof_cot is not None:
        updates["proof.cot"] = proof_cot
    if proof_full is not None:
        updates["proof.full"] = proof_full
    if proof_ref is not None:
        updates["proof.ref"] = proof_ref
    if preliminaries is not None:
        updates["preliminaries"] = preliminaries
    if progresses is not None:
        updates["progresses"] = progresses
    if validation_issues is not None:
        updates["validation.issues"] = validation_issues
    if validation_responses is not None:
        updates["validation.responses"] = validation_responses

    if not updates:
        raise ValueError("No updates provided for statement update.")

    # Load existing object to create a placeholder for the change
    existing = load_object(id)

    # Create a minimal statement object for the change (just need the id)
    placeholder = type_statement(
        id=id,
        type=existing["type"],
        conclusion=existing["conclusion"]
    )

    # Create change object
    change = type_object_change(
        change_type="update",
        obj=placeholder,
        updates=updates
    )

    if root_change:
        log_id, _, modified_ids = handle_changes([change])
        fields_str = _format_update_fields(updates)
        return (log_id, fields_str)
    else:
        return (id, [change])


def build_args_from_parsed(args) -> dict:
    """Convert parsed args to function kwargs.

    Args:
        args: Parsed argparse namespace

    Returns:
        Dict of kwargs for handle_statement
    """
    kwargs = {}

    kwargs["id"] = args.id

    # Single-value fields
    if args.type is not None:
        kwargs["type"] = args.type
    if args.conclusion is not None:
        kwargs["conclusion"] = args.conclusion
    if args.status is not None:
        kwargs["status"] = args.status
    if args.reliability is not None:
        kwargs["reliability"] = args.reliability
    if args.proof_full is not None:
        kwargs["proof_full"] = args.proof_full

    # Multiple-value fields (mode + values)
    if args.hypothesis:
        mode = args.hypothesis[0]
        values = args.hypothesis[1:]
        kwargs["hypothesis"] = (mode, values)
    if args.proof_cot:
        mode = args.proof_cot[0]
        values = args.proof_cot[1:]
        kwargs["proof_cot"] = (mode, values)
    if args.proof_ref:
        mode = args.proof_ref[0]
        values = args.proof_ref[1:]
        kwargs["proof_ref"] = (mode, values)
    if args.preliminaries:
        mode = args.preliminaries[0]
        values = args.preliminaries[1:]
        kwargs["preliminaries"] = (mode, values)
    if args.progresses:
        mode = args.progresses[0]
        values = args.progresses[1:]
        kwargs["progresses"] = (mode, values)
    if args.validation_issues:
        mode = args.validation_issues[0]
        values = args.validation_issues[1:]
        kwargs["validation_issues"] = (mode, values)
    if args.validation_responses:
        mode = args.validation_responses[0]
        values = args.validation_responses[1:]
        kwargs["validation_responses"] = (mode, values)

    return kwargs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create or update a statement")

    # Mode identifier
    parser.add_argument('--id', type=str, default=None,
                        help='Statement ID for update mode; omit for create mode')

    # Single-value params
    parser.add_argument('--type', type=str, choices=VALID_TYPES,
                        help='Statement type (required for create mode)')
    parser.add_argument('--conclusion', nargs='+', type=str,
                        help='Conclusion (required for create mode)')
    parser.add_argument('--status', type=str,
                        help='Statement status')
    parser.add_argument('--reliability', type=float,
                        help='Reliability score (0.0 to 1.0)')
    parser.add_argument('--proof.full', type=str, dest='proof_full',
                        help='Full proof text')

    # Multiple-value params (mode + values)
    parser.add_argument('--hypothesis', nargs='+', type=str,
                        help='Mode (Overwrite/Append) followed by hypothesis items')
    parser.add_argument('--proof.cot', nargs='+', type=str, dest='proof_cot',
                        help='Mode (Overwrite/Append) followed by chain-of-thought steps')
    parser.add_argument('--proof.ref', nargs='+', type=str, dest='proof_ref',
                        help='Mode (Overwrite/Append) followed by references')
    parser.add_argument('--preliminaries', nargs='+', type=str,
                        help='Mode (Overwrite/Append) followed by preliminary statement IDs')
    parser.add_argument('--progresses', nargs='+', type=str,
                        help='Mode (Overwrite/Append) followed by progress items')
    parser.add_argument('--validation.issues', nargs='+', type=str, dest='validation_issues',
                        help='Mode (Overwrite/Append) followed by validation issues')
    parser.add_argument('--validation.responses', nargs='+', type=str, dest='validation_responses',
                        help='Mode (Overwrite/Append) followed by validation responses')

    args = parser.parse_args()

    kwargs = build_args_from_parsed(args)

    # Determine mode and validate
    if args.id is None:
        # Create mode - type and conclusion required
        if args.type is None or args.conclusion is None:
            parser.error("--type and --conclusion are required for create mode (when --id is not provided)")

    result = handle_statement(**kwargs)

    if args.id is None:
        # Create mode: result is statement_id
        print(f"Created statement: {result}")
    else:
        # Update mode: result is (log_id, fields_str)
        log_id, fields_str = result
        print(f"Updated {args.id} {fields_str} (log: {log_id})")
