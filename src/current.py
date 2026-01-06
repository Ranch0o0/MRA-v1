import json
import glob
import os

from utils import PROJECT_ROOT, OBJECT_FOLDERS, IDManager


def load_all_problems() -> list[dict]:
    """Load all problem JSON files from the problems folder."""
    folder = OBJECT_FOLDERS["p"]
    pattern = os.path.join(folder, "p-*.json")
    problems = []

    for file_path in glob.glob(pattern):
        with open(file_path, "r") as f:
            problems.append(json.load(f))

    # Sort by id for consistent ordering
    problems.sort(key=lambda x: x["id"])
    return problems


def load_all_statements() -> list[dict]:
    """Load all statement JSON files from the statements folder."""
    folder = OBJECT_FOLDERS["s"]
    pattern = os.path.join(folder, "s-*.json")
    statements = []

    for file_path in glob.glob(pattern):
        with open(file_path, "r") as f:
            statements.append(json.load(f))

    # Sort by id for consistent ordering
    statements.sort(key=lambda x: x["id"])
    return statements


def get_actionable_problems(problems: list[dict]) -> list[dict]:
    """Filter problems that are actionable.

    Actionable problems are:
    - status = "unresolved"
    - preliminaries = [] (no dependencies)
    """
    return [
        p for p in problems
        if p.get("status") == "unresolved" and p.get("preliminaries", []) == []
    ]


def get_pending_statements(statements: list[dict]) -> list[dict]:
    """Filter statements that are pending (un-proved).

    Pending statements are:
    - status = "pending"
    """
    return [s for s in statements if s.get("status") == "pending"]


def display_problems(problems: list[dict]) -> None:
    """Display problem info: id, objectives, progresses."""
    print("=== Actionable Problems ===")

    if not problems:
        print("\n(none)")
        return

    for p in problems:
        print(f"\n[{p['id']}]")

        # Objectives
        print("  Objectives:")
        objectives = p.get("objectives", [])
        if objectives:
            for obj in objectives:
                print(f"    - {obj}")
        else:
            print("    (none)")

        # Progresses
        print("  Progresses:")
        progresses = p.get("progresses", [])
        if progresses:
            for prog in progresses:
                print(f"    - {prog}")
        else:
            print("    (none)")


def display_statements(statements: list[dict]) -> None:
    """Display statement info: id, conclusion."""
    print("=== Pending Statements ===")

    if not statements:
        print("\n(none)")
        return

    for s in statements:
        print(f"\n[{s['id']}]")

        # Conclusion
        print("  Conclusion:")
        conclusions = s.get("conclusion", [])
        if conclusions:
            for conc in conclusions:
                print(f"    - {conc}")
        else:
            print("    (none)")


def is_puzzle_initialized() -> bool:
    """Check if the puzzle has been initialized.

    Returns True if log ID > l-000 (meaning at least one operation has been logged).
    """
    id_manager = IDManager()
    current_log_id = id_manager.current_ids.get("l", "l-000")
    return current_log_id != "l-000"


def show_current_status() -> None:
    """Main function to display current status."""
    # Load all objects
    problems = load_all_problems()
    statements = load_all_statements()

    # Filter
    actionable_problems = get_actionable_problems(problems)
    pending_statements = get_pending_statements(statements)

    # Check for edge case: no actionable items
    if not actionable_problems and not pending_statements:
        if not is_puzzle_initialized():
            # No logs yet - puzzle hasn't been initialized
            print("=== Status: Not Initialized ===")
            print("\nThe puzzle has not been initialized yet.")
            print("Please run the initializer agent or use prob_init.py to start.")
        else:
            # Logs exist but no pending work - puzzle is solved
            print("=== Status: Puzzle Solved ===")
            print("\nAll problems have been resolved and all statements have been proved.")
            print("The puzzle solution should be available in the resolved problem(s).")
        return

    # Normal case: display actionable items
    display_problems(actionable_problems)
    print()  # separator
    display_statements(pending_statements)


if __name__ == "__main__":
    show_current_status()
