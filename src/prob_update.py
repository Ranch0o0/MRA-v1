import argparse

from utils import update_objects


def update_problem(
    obj_id: str,
    updates: dict,
    root_change: bool = True
) -> str | tuple[str, dict]:
    """Update a problem object.

    Args:
        obj_id: Problem ID (e.g., "p-001")
        updates: Dict of field paths to new values
        root_change: If True, commit update and log; if False, return update for parent

    Returns:
        If root_change=True: Log ID
        If root_change=False: Tuple of (obj_id, updates) for parent to handle
    """
    if not obj_id.startswith("p-"):
        raise ValueError(f"Invalid problem ID: {obj_id}. Expected 'p-XXX' format.")

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
    if args.motivation is not None:
        updates["motivation"] = args.motivation
    if args.priority is not None:
        updates["priority"] = args.priority
    if args.solution_full is not None:
        updates["solution.full"] = args.solution_full

    # Multiple-value fields
    if args.preliminary:
        mode = args.preliminary[0]  # Will be lowercased in apply_updates
        values = args.preliminary[1:]
        updates["preliminary"] = (mode, values)
    if args.solution_cot:
        mode = args.solution_cot[0]
        values = args.solution_cot[1:]
        updates["solution.cot"] = (mode, values)

    return updates


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update a problem")

    # Required
    parser.add_argument('--id', type=str, required=True, help='Problem ID to update')

    # Single-value params
    parser.add_argument('--status', type=str, help='New status value')
    parser.add_argument('--motivation', type=str, help='Problem motivation')
    parser.add_argument('--priority', type=str, help='Problem priority')
    parser.add_argument('--solution.full', type=str, dest='solution_full',
                        help='Full solution text')

    # Multiple-value params (mode + values)
    parser.add_argument('--preliminary', nargs='+', type=str,
                        help='Mode (Overwrite/Append) followed by preliminary steps')
    parser.add_argument('--solution.cot', nargs='+', type=str, dest='solution_cot',
                        help='Mode (Overwrite/Append) followed by chain-of-thought steps')

    args = parser.parse_args()

    updates = build_updates_from_args(args)

    if not updates:
        print("No updates specified. Use --help to see available options.")
    else:
        log_id = update_problem(args.id, updates)
        print(f"Updated problem {args.id} (log: {log_id})")
