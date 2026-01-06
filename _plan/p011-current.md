# Add a script for show current status

## Meta Info
- **Script** `src/current.py`

## Instruction
Main purpose of this script is to run through all unresolved problems and statement and present their information to the orchestrator.

1. Problems
- Run through all problems and find those with
    - `status = "unresolved"` <- Problems to be handled
    - `preliminaries = []` <- No dependencies implies that these problems are to be solved first.
- Print the following info:
    - Problem id.
    - Objectives.
    - Progresses.

2. Statements
- Run through all problems and find those with
    - `type != "pending"` <- Un-proved statements.
- Print the following info:
    - Statement id.
    - Conclusion.

## Test
- Test on the current setup.

---

## Implementation Plan

### Overview
Create `src/current.py` - a script that displays the current status of unresolved problems and pending statements to help the orchestrator understand what needs attention.

### Clarifications from User
- **Statement filter**: Use `status = "pending"` to identify un-proved statements (not `type != "pending"`)
- The script should show items that **need attention**:
  - Problems: unresolved with no dependencies
  - Statements: pending (un-proved)

### Step 1: Imports and Setup
- Import `os`, `json`, and `glob` for file operations
- Use `PROJECT_ROOT` and `OBJECT_FOLDERS` from `utils.py` for consistent path handling

### Step 2: Load All Objects Function
Create helper functions to load all objects of a specific type:
```python
def load_all_problems() -> list[dict]:
    """Load all problem JSON files from the problems folder."""

def load_all_statements() -> list[dict]:
    """Load all statement JSON files from the statements folder."""
```

### Step 3: Filter Functions
Create filter functions based on the criteria:

**For Problems:**
```python
def get_actionable_problems(problems: list[dict]) -> list[dict]:
    """
    Filter problems that are:
    - status = "unresolved"
    - preliminaries = [] (no dependencies)
    """
```

**For Statements:**
```python
def get_pending_statements(statements: list[dict]) -> list[dict]:
    """
    Filter statements that are:
    - status = "pending" (un-proved)
    """
```

### Step 4: Display Functions
Create formatted display functions:

**For Problems:**
```python
def display_problems(problems: list[dict]) -> None:
    """
    Print problem info:
    - Problem id
    - Objectives (list)
    - Progresses (list)
    """
```
Output format:
```
=== Actionable Problems ===

[p-002]
  Objectives:
    - Sub-objective 1
  Progresses:
    (none)

[p-003]
  Objectives:
    - Simple objective
  Progresses:
    (none)
```

**For Statements:**
```python
def display_statements(statements: list[dict]) -> None:
    """
    Print statement info:
    - Statement id
    - Conclusion (list)
    """
```
Output format:
```
=== Pending Statements ===

[s-004]
  Conclusion:
    - New hypothesis item
```

### Step 5: Main Function
```python
def show_current_status() -> None:
    """Main function to display current status."""
    # Load all objects
    problems = load_all_problems()
    statements = load_all_statements()

    # Filter
    actionable_problems = get_actionable_problems(problems)
    pending_statements = get_pending_statements(statements)

    # Display
    display_problems(actionable_problems)
    print()  # separator
    display_statements(pending_statements)

if __name__ == "__main__":
    show_current_status()
```

### Step 6: Testing
Run the script on the current setup:
```bash
venv-python src/current.py
```

Expected output based on current data:
- **Problems**: p-002, p-003 (both unresolved with empty preliminaries)
- **Statements**: s-004 (status = "pending")

### File Structure
```
src/
├── current.py      # NEW - status display script
├── utils.py        # existing - reuse PROJECT_ROOT, OBJECT_FOLDERS
├── ...
```

### Dependencies
- Reuse constants from `utils.py`:
  - `PROJECT_ROOT`
  - `OBJECT_FOLDERS`
  - `IDManager`
- Standard library only: `os`, `json`, `glob`

---

## Implementation Notes (Post-Implementation)

### Additional Feature: Edge Case Handling
Added logic to handle two edge cases when no actionable problems or pending statements exist:

**1. Puzzle Not Initialized** (`log_id == "l-000"`)
```
=== Status: Not Initialized ===

The puzzle has not been initialized yet.
Please run the initializer agent or use prob_init.py to start.
```

**2. Puzzle Solved** (`log_id > "l-000"` but no pending work)
```
=== Status: Puzzle Solved ===

All problems have been resolved and all statements have been proved.
The puzzle solution should be available in the resolved problem(s).
```

### Added Function
```python
def is_puzzle_initialized() -> bool:
    """Check if the puzzle has been initialized.

    Returns True if log ID > l-000 (meaning at least one operation has been logged).
    """
    id_manager = IDManager()
    current_log_id = id_manager.current_ids.get("l", "l-000")
    return current_log_id != "l-000"
```

### Updated Main Function Logic
```python
def show_current_status() -> None:
    # ... load and filter ...

    # Check for edge case: no actionable items
    if not actionable_problems and not pending_statements:
        if not is_puzzle_initialized():
            # No logs yet - puzzle hasn't been initialized
            print("=== Status: Not Initialized ===")
            ...
        else:
            # Logs exist but no pending work - puzzle is solved
            print("=== Status: Puzzle Solved ===")
            ...
        return

    # Normal case: display actionable items
    ...
```

### Status: COMPLETED
