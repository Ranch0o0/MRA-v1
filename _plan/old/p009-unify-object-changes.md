# Unify the object changes

## Meta Info
- **Scripts to change** `src/cus_types.py`, `src/prob_init.py`, and `scr/utils.py`
- **Scripts to be removed** `src/prob_update.py`, `src/state_init.py`, and `src/state_update.py`
- **Scripts to be added** `src/prob.py` and `src/state.py`

## Param types
For the params that can be added via terminal arguments, I am expecting two types:
- Single: this type of params is expected to receive a single value, and the corresponding properties in the problem or statement object is expected to be a single-valued (i.e. string or number) and is expected to be modified to this single value.
- Multiple: this type of params is expected to receive a sequence of values.
    - The corresponding properties in the problem or statement object is expected to be a list.
    - The first values is expected to indicate the mode:
        - "Overwrite": Create a new list by the following sequence of values
        - "Append": Simply append all following sequence of values to the current list.

## Instruction
1. `src/cus_types.py`
- Create a custom type `type_object_change`
    - Has a `type` property, expecting "create" or "update", indicating which type of changes.
    - Has an `object` property which is either of type `type_problem` or `type_statement`, recording the (pointer to) object that is to be changed.
**Note** There are some changes in `cus_types_main.py` for the custom dataclass (alredy done by myself)
- `type_argument`
    - Add a new key `ref`
- `type_problem`
    - Deleted `motivation`
    - Change the key `prelimilary` to `prelimilaries`
    - Add new keys `progresses` and `summary`
- `type_statement`
    - Deleted `dependencies`

2. `src/utils.py`
- Unify the object commit and object update: make a single function to handle both creating and updating.
- Param: tasks: list[type_object_change]
- Preserve the logging functionality as before.

3. Create unified `src/prob.py` (and delete `src/prob_update.py`)
- Use the id arg to decide whether to create or update.
    - If no id arg, process creation logic.
    - If id arg is provided, but is not in valid problem id format or not linked to an existing problem object (compare with current max problem id), raise error.
    - If id arg is provided and is valid, process update logic.
- For the problem creating logic, handles the nested statement creation logic as in the current `src/prob_init.py` script.
    - **Note** Now the script `src/prob.py` is designed to only handle the problem creating after initialization, so in nested statement creation, the status should be set as "normal".
- Updated terminal args:
    - id: str
        - This param is must-include: it identifies which object to update.
    - hypothesis: list[str]
        - mode: multiple
    - objectives: list[str]
        - mode: multiple
    - status: str
        - mode: single
    - priority: str
        - mode: single
    - summary: str
        - mode: single
    - prelimilaries: list[str]
        - mode: multiple
    - progresses: list[str]
        - mode: multiple
    - solution.cot: list[str]
        - mode: multiple
    - solution.full: str
        - mode: single
    - solution.ref: list[str]
        - mode: multiple

4. Simplify `src/prob_init.py`
- Only keep the current functionality for initialing the problem from a puzzle.
- Can remove the `initial` arg, as this script will only be run once per puzzle.
- Check and determine if further simplification can be made.

5. Create unified `src/state.py` (and delete `src/state_init.py` and `src/state_update.py`)
- Use the id arg to decide whether to create or update.
    - If no id arg, process creation logic.
    - If id arg is provided, but is not in valid problem id format or not linked to an existing problem object (compare with current max problem id), raise error.
    - If id arg is provided and is valid, process update logic.
- Updated terminal args:
    - id: str
        - This param is must-include: it identifies which object to update.
    - type: str
        - mode: single 
    - conclusion: str
        - mode: single
    - status: str
        - mode: single
    - reliability: float
        - mode: single
    - hypothesis: list[str]
        - mode: multiple
    - proof.cot: list[str]
        - mode: multiple
    - proof.full: str
        - mode: single
    - proof.ref: list[str]
        - mode: multiple

**Important**
- Please check if there are missing properties for the custom type `type_problem` and `type_statement`.
- Note the `stats` property is omitted deliberately, as it is not supposed to be modified directly via agents.

---

## Implementation Plan

### Clarifications from Discussion
1. **Create mode for `prob.py`**: Only `objectives` is required; `hypothesis` is optional
2. **ID parameter**: Optional - no id = create mode, valid id = update mode
3. **Spelling**: Use correct spelling `preliminaries` (not `prelimilaries`)
4. **Type style**: Use `@dataclass` for `type_object_change`
5. **Create mode for `state.py`**: `type` and `conclusion` are required
6. **Mixed operations**: `handle_changes` supports mixed create/update in a single call, but `prob.py` and `state.py` handle only one main object (with possible nested operations)
7. **ref field**: Rename `reference` to `ref` in `type_argument`

### Step 1: Update `src/cus_types_main.py`

**1.1 Rename `reference` to `ref` in `type_argument`**
```python
@dataclass
class type_argument:
    cot: list[str] = field(default_factory=list)
    full: str = ""
    ref: list[str] = field(default_factory=list)  # renamed from 'reference'
```

**1.2 Create `type_object_change` dataclass**
```python
from typing import Union

@dataclass
class type_object_change:
    type: str  # "create" or "update"
    object: Union['type_problem', 'type_statement']  # the object to be changed
```

Note: Place this after `type_problem` and `type_statement` definitions to avoid forward reference issues, or use string annotation `'type_problem'`.

### Step 2: Update `src/utils.py`

**2.1 Create unified `handle_changes` function**

Replace the separate `commit_objects` and `update_objects` with a unified function:

```python
from cus_types_main import type_object_change

def handle_changes(tasks: list[type_object_change]) -> tuple[str, list[str], list[str]]:
    """Unified function to handle both creation and update of objects.

    Args:
        tasks: List of type_object_change objects, each containing:
            - type: "create" or "update"
            - object: The object data (type_problem or type_statement)

    Returns:
        Tuple of (log_id, list of created IDs, list of modified IDs)

    Process:
        1. Generate log_id
        2. For updates: create backup folder and backup files
        3. Process each task:
           - "create": write new object file
           - "update": load, apply updates, write back
        4. Write log entry with both created and modified IDs
    """
```

**Implementation details:**
- Generate log_id at the beginning
- Create backup folder `contents/history/{log_id}/` if there are any updates
- For "create" tasks: write object to appropriate folder based on ID prefix
- For "update" tasks:
  - Load existing object
  - Backup to history folder
  - Apply updates using existing `apply_updates` function
  - Write updated object back
- Write single log entry with both `creation` and `modification` lists
- Return (log_id, created_ids, modified_ids)

**2.2 Keep existing helper functions**
- Keep `apply_updates` - it's still needed
- Keep `load_object` - still needed
- Keep `get_object_type_from_id` - still needed
- Keep `IDManager` and `LogManager` classes
- Keep `commit_objects` and `update_objects` as deprecated but functional for backward compatibility (optional, can remove if no other code depends on them)

### Step 3: Create `src/prob.py`

**3.1 Structure overview**
```python
import argparse
import re
from dataclasses import asdict
from typing import Optional

from cus_types_main import type_problem, type_statement, type_object_change
from utils import IDManager, handle_changes, load_object, OBJECT_FOLDERS
```

**3.2 Helper functions**
- `parse_statement_id(text: str) -> str | None` - reuse from prob_init.py
- `load_statement_conclusion(statement_id: str) -> str | None` - reuse from prob_init.py
- `process_hypothesis_item(item: str) -> tuple[str, list[type_object_change]]` - modified to return type_object_change list, status="normal" for new statements
- `validate_problem_id(obj_id: str) -> bool` - validate format and existence

**3.3 Main function `handle_problem`**
```python
def handle_problem(
    id: Optional[str] = None,
    objectives: Optional[list[str]] = None,
    hypothesis: Optional[list[str]] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    summary: Optional[str] = None,
    preliminaries: Optional[tuple[str, list[str]]] = None,  # (mode, values)
    progresses: Optional[tuple[str, list[str]]] = None,
    solution_cot: Optional[tuple[str, list[str]]] = None,
    solution_full: Optional[str] = None,
    solution_ref: Optional[tuple[str, list[str]]] = None,
    root_change: bool = True
) -> str | tuple[str, list[type_object_change]]:
    """Handle problem creation or update.

    Args:
        id: Problem ID for update mode; None for create mode
        ... (other fields)
        root_change: If True, commit changes; if False, return changes for parent

    Returns:
        If root_change=True: log_id (for update) or problem_id (for create)
        If root_change=False: tuple of (problem_id, list of type_object_change)
    """
```

**3.4 Create mode logic (id is None)**
- Validate: `objectives` is required
- Process hypothesis items (if provided) - create nested statements with status="normal"
- Generate new problem ID
- Build problem object with processed hypothesis and objectives
- Collect all type_object_change items (nested statements + problem)
- If root_change: call `handle_changes` and return problem_id
- If not root_change: return (problem_id, changes_list)

**3.5 Update mode logic (id is provided)**
- Validate ID format: must match `p-XXX` pattern
- Validate ID exists: compare with current max ID from IDManager
- Build updates dict from provided arguments
- Handle nested fields (solution.cot, solution.full, solution.ref)
- Create type_object_change with type="update"
- If root_change: call `handle_changes` and return log_id
- If not root_change: return (id, changes_list)

**3.6 Argument parser**
```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create or update a problem")

    # Mode identifier
    parser.add_argument('--id', type=str, default=None,
                        help='Problem ID for update mode; omit for create mode')

    # Multiple-value params
    parser.add_argument('--hypothesis', nargs='+', type=str)
    parser.add_argument('--objectives', nargs='+', type=str)
    parser.add_argument('--preliminaries', nargs='+', type=str,
                        help='Mode (Overwrite/Append) followed by values')
    parser.add_argument('--progresses', nargs='+', type=str,
                        help='Mode (Overwrite/Append) followed by values')
    parser.add_argument('--solution.cot', nargs='+', type=str, dest='solution_cot')
    parser.add_argument('--solution.ref', nargs='+', type=str, dest='solution_ref')

    # Single-value params
    parser.add_argument('--status', type=str)
    parser.add_argument('--priority', type=str)
    parser.add_argument('--summary', type=str)
    parser.add_argument('--solution.full', type=str, dest='solution_full')
```

### Step 4: Simplify `src/prob_init.py`

**4.1 Keep only puzzle initialization logic**
- Remove the `--initial` argument (always True for this script)
- Keep `create_problem` function but simplify:
  - Always set `initial=True` internally
  - Statements created with status="true" (assumption type)
- This script is only for the very first problem creation from a puzzle

**4.2 Simplified structure**
```python
def create_initial_problem(
    hypothesis: list[str],
    objectives: list[str],
    root_change: bool = True
) -> str | tuple[str, list[type_object_change]]:
    """Create the initial problem from a puzzle.

    This is the entry point for puzzle initialization.
    All hypothesis items are treated as assumptions (status='true').
    """
```

**4.3 Argument parser**
```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize problem from puzzle")
    parser.add_argument('--hypothesis', nargs='+', type=str, required=True)
    parser.add_argument('--objectives', nargs='+', type=str, required=True)
```

### Step 5: Create `src/state.py`

**5.1 Structure overview**
```python
import argparse
from dataclasses import asdict
from typing import Optional

from cus_types_main import type_statement, type_object_change
from utils import IDManager, handle_changes, load_object
```

**5.2 Validation helper**
```python
def validate_statement_id(obj_id: str) -> bool:
    """Validate statement ID format and existence."""
```

**5.3 Main function `handle_statement`**
```python
def handle_statement(
    id: Optional[str] = None,
    type: Optional[str] = None,
    conclusion: Optional[list[str]] = None,
    status: Optional[str] = None,
    reliability: Optional[float] = None,
    hypothesis: Optional[tuple[str, list[str]]] = None,  # (mode, values)
    proof_cot: Optional[tuple[str, list[str]]] = None,
    proof_full: Optional[str] = None,
    proof_ref: Optional[tuple[str, list[str]]] = None,
    root_change: bool = True
) -> str | tuple[str, list[type_object_change]]:
    """Handle statement creation or update.

    Args:
        id: Statement ID for update mode; None for create mode
        type: Statement type (required for create mode)
        conclusion: Conclusion list (required for create mode)
        ... (other fields)
        root_change: If True, commit changes; if False, return changes for parent
    """
```

**5.4 Create mode logic (id is None)**
- Validate: `type` and `conclusion` are required
- Generate new statement ID
- Build statement object with provided fields
- Create type_object_change with type="create"
- If root_change: call `handle_changes` and return statement_id
- If not root_change: return (statement_id, changes_list)

**5.5 Update mode logic (id is provided)**
- Validate ID format: must match `s-XXX` pattern
- Validate ID exists
- Build updates dict from provided arguments
- Handle nested fields (proof.cot, proof.full, proof.ref)
- Create type_object_change with type="update"
- If root_change: call `handle_changes` and return log_id
- If not root_change: return (id, changes_list)

**5.6 Argument parser**
```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create or update a statement")

    # Mode identifier
    parser.add_argument('--id', type=str, default=None)

    # Single-value params
    parser.add_argument('--type', type=str)
    parser.add_argument('--conclusion', nargs='+', type=str)  # treated as single for update
    parser.add_argument('--status', type=str)
    parser.add_argument('--reliability', type=float)
    parser.add_argument('--proof.full', type=str, dest='proof_full')

    # Multiple-value params
    parser.add_argument('--hypothesis', nargs='+', type=str)
    parser.add_argument('--proof.cot', nargs='+', type=str, dest='proof_cot')
    parser.add_argument('--proof.ref', nargs='+', type=str, dest='proof_ref')
```

### Step 6: Delete deprecated files

After successful implementation and testing:
- Delete `src/prob_update.py`
- Delete `src/state_init.py`
- Delete `src/state_update.py`

### Step 7: Update any imports in other files

Check and update imports in any files that reference the deleted modules:
- `prob_init.py` imports `state_init.py` - update to use `state.py`
- Any other files importing from deleted modules

### Implementation Order

1. **Phase 1**: Update `cus_types_main.py` (Steps 1.1, 1.2)
2. **Phase 2**: Update `utils.py` with `handle_changes` (Step 2)
3. **Phase 3**: Create `state.py` (Step 5) - simpler, no nested logic
4. **Phase 4**: Simplify `prob_init.py` (Step 4)
5. **Phase 5**: Create `prob.py` (Step 3) - depends on state.py for nested statements
6. **Phase 6**: Delete deprecated files (Step 6)
7. **Phase 7**: Update imports and test (Step 7)

### Testing Checklist

- [ ] `type_object_change` dataclass works correctly
- [ ] `handle_changes` handles create-only tasks
- [ ] `handle_changes` handles update-only tasks
- [ ] `handle_changes` handles mixed create+update tasks
- [ ] `prob.py` create mode works (no id)
- [ ] `prob.py` update mode works (with id)
- [ ] `prob.py` rejects invalid/non-existent IDs
- [ ] `state.py` create mode works
- [ ] `state.py` update mode works
- [ ] `prob_init.py` still works for puzzle initialization
- [ ] Log entries are correctly formatted
- [ ] Backup files are created for updates
- [ ] Nested statement creation works in `prob.py`
