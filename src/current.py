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


def get_actionable_problems(problems: list[dict], statements: list[dict]) -> list[dict]:
    """Filter problems that are actionable.

    Actionable problems are:
    - status = "unresolved"
    - All preliminaries have their required status:
      - Preliminary problems: status = "resolved"
      - Preliminary statements: status = "true"
    """
    # Create lookup dicts for quick status checks
    problem_lookup = {p["id"]: p for p in problems}
    statement_lookup = {s["id"]: s for s in statements}

    actionable = []
    for p in problems:
        # First filter: status must be "unresolved"
        if p.get("status") != "unresolved":
            continue

        # Second filter: check preliminaries (can be problems or statements)
        preliminaries = p.get("preliminaries", [])
        all_prelim_resolved = True

        for prelim_id in preliminaries:
            # Check if it's a problem
            if prelim_id.startswith("p-"):
                prelim = problem_lookup.get(prelim_id)
                if prelim and prelim.get("status") != "resolved":
                    all_prelim_resolved = False
                    break
            # Check if it's a statement
            elif prelim_id.startswith("s-"):
                prelim = statement_lookup.get(prelim_id)
                if prelim and prelim.get("status") != "true":
                    all_prelim_resolved = False
                    break

        if all_prelim_resolved:
            actionable.append(p)

    return actionable


def get_actionable_statements(statements: list[dict]) -> list[dict]:
    """Filter statements that need attention (pending or validating).

    Actionable statements are:
    - status = "pending" OR "validating"
    - All preliminary statements (if any) have status = "true"
    """
    actionable = []

    # Create a lookup dict for quick status checks
    statement_lookup = {s["id"]: s for s in statements}

    for s in statements:
        status = s.get("status")

        # First filter: status must be "pending" or "validating"
        if status not in ("pending", "validating"):
            continue

        # Second filter: check preliminaries
        preliminaries = s.get("preliminaries", [])
        all_prelim_resolved = True

        for prelim_id in preliminaries:
            prelim = statement_lookup.get(prelim_id)
            if prelim and prelim.get("status") != "true":
                all_prelim_resolved = False
                break

        if all_prelim_resolved:
            actionable.append(s)

    return actionable


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
    """Display statement info: id, conclusion, and validation status if applicable."""
    print("=== Actionable Statements ===")

    if not statements:
        print("\n(none)")
        return

    for s in statements:
        print(f"\n[{s['id']}]")

        # Status indicator
        status = s.get("status", "pending")

        # Conclusion
        print("  Conclusion:")
        conclusions = s.get("conclusion", [])
        if conclusions:
            for conc in conclusions:
                print(f"    - {conc}")
        else:
            print("    (none)")

        # Progresses
        print("  Progresses:")
        progresses = s.get("progresses", [])
        if progresses:
            for prog in progresses:
                print(f"    - {prog}")
        else:
            print("    (none)")

        # For validating statements, show validation status
        if status == "validating":
            validation = s.get("validation", {})
            issues = validation.get("issues", [])
            responses = validation.get("responses", [])

            len_issues = len(issues)
            len_responses = len(responses)

            print("  Validation Status:")
            if len_issues > len_responses:
                # Unresolved issues exist
                print(f"    [!] UNRESOLVED ISSUES: {len_issues - len_responses} issue(s) awaiting response")
                print(f"    (issues: {len_issues}, responses: {len_responses})")
            elif len_issues == len_responses:
                # All issues addressed, awaiting checker
                print(f"    [*] AWAITING CHECKER: All {len_issues} issue(s) have responses")
                print(f"    Call checker to examine the latest response")
            else:
                # Error: more responses than issues
                print(f"    [WARNING] INVALID STATE: More responses ({len_responses}) than issues ({len_issues})")
                print(f"    Please inspect this statement manually")


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
    actionable_problems = get_actionable_problems(problems, statements)
    actionable_statements = get_actionable_statements(statements)

    # Check for edge case: no actionable items
    if not actionable_problems and not actionable_statements:
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
    display_statements(actionable_statements)


if __name__ == "__main__":
    show_current_status()
