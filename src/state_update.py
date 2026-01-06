import argparse

from utils import update_objects


def update_statement(
    obj_id: str,
    updates: dict,
    root_change: bool = True
) -> str | tuple[str, dict]:
    """Update a statement object.

    Args:
        obj_id: Statement ID (e.g., "s-001")
        updates: Dict of field paths to new values
        root_change: If True, commit update and log; if False, return update for parent

    Returns:
        If root_change=True: Log ID
        If root_change=False: Tuple of (obj_id, updates) for parent to handle
    """
    if not obj_id.startswith("s-"):
        raise ValueError(f"Invalid statement ID: {obj_id}. Expected 's-XXX' format.")

    if root_change:
        log_id, _ = update_objects([(obj_id, updates)])
        return log_id
    else:
        return (obj_id, updates)


def build_updates_from_args(args) -> dict:
    """Convert parsed args to updates dict.

    Handles:
    - Single-value fields: directly set the value
    - Multiple-value fields: parse mode and values

    Returns:
        Dict mapping field paths to values or (mode, values) tuples
    """
    updates = {}

    # Single-value fields
    if args.status is not None:
        updates["status"] = args.status
    if args.proof_full is not None:
        updates["proof.full"] = args.proof_full

    # Multiple-value fields
    if args.dependencies:
        mode = args.dependencies[0]  # Will be lowercased in apply_updates
        values = args.dependencies[1:]
        updates["dependencies"] = (mode, values)
    if args.proof_cot:
        mode = args.proof_cot[0]
        values = args.proof_cot[1:]
        updates["proof.cot"] = (mode, values)

    return updates


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update a statement")

    # Required
    parser.add_argument('--id', type=str, required=True, help='Statement ID to update')

    # Single-value params
    parser.add_argument('--status', type=str, help='New status value')
    parser.add_argument('--proof.full', type=str, dest='proof_full', help='Full proof text')

    # Multiple-value params (mode + values)
    parser.add_argument('--dependencies', nargs='+', type=str,
                        help='Mode (Overwrite/Append) followed by dependency IDs')
    parser.add_argument('--proof.cot', nargs='+', type=str, dest='proof_cot',
                        help='Mode (Overwrite/Append) followed by chain-of-thought steps')

    args = parser.parse_args()

    updates = build_updates_from_args(args)

    if not updates:
        print("No updates specified. Use --help to see available options.")
    else:
        log_id = update_statement(args.id, updates)
        print(f"Updated statement {args.id} (log: {log_id})")
