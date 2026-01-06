# Develop the update functionality

## Meta Info
- **Scripts** `src/utils.py` (modify), `src/prob_update.py` (create), `src/state_update.py` (create)
- **Save paths**
    - problems: `contents/problem`
    - statement: `contents/statement`
    - old version: `contents/history/{{log_id}}/`

## Principles
- Only the log Manager can update the json files: this is to make convenience for logging and version control.
- Functions in `src/prob_update.py` and `src/state_update.py` only pushes update requests or return list of updates (according to `root_change` param). Chief `_plan/p006-log.md` for old implementation.

## Param types
For the params that can be added via terminal arguments, I am expecting two types:
- Single: this type of params is expected to receive a single value, and the corresponding properties in the problem or statement object is expected to be a single-valued (i.e. string or number) and is expected to be modified to this single value.
- Multiple: this type of params is expected to receive a sequence of values.
    - The corresponding properties in the problem or statement object is expected to be a list.
    - The first values is expected to indicate the mode:
        - "Overwrite": Create a new list by the following sequence of values
        - "Append": Simply append all following sequence of values to the current list.

## Instructions
1. `src/prob_update.py`
- In the main block, create the following params: 
    - id: str
        - This param is must-include: it identifies which object to update.
    - status: str
        - mode: single
    - motivation: str
        - mode: single
    - priority: str
        - mode: single
    - prelimilary: list[str]
        - mode: multiple
    - solution_cot: list[str]
        - mode: multiple
    - solution_full: str
        - mode: single

2. `src/state_update.py`
- In the main block, create the following params: 
    - id: str
        - This param is must-include: it identifies which object to update.
    - status: str
        - mode: single
    - dependencies: list[str]
        - mode: multiple
    - proof_cot: list[str]
        - mode: multiple
    - proof_full: str
        - mode: single

3. `src/utils.py`
- Create a new function to handle object updates.
- To manage the history:
    - In `contents/history/log.jsonl`, record the list of changed object ids AND current indices.
    - Each log entry includes a `"current"` field with compact format: `[p-XXX, s-XXX, e-XXX]` (no log index).
    - Example: `{"l-002": {"creation": [], "modification": ["s-001"]}, "current": ["p-001", "s-013", "e-000"]}`
    - If the update list is non-empty
        - Create a folder `contents/history/{{log_id}}/`
        - Copy ALL the objects that will be updated into this folder.
        - **Note** Make sure to first copy the old object files before updating them.

---

## Implementation Plan

### Design Decisions (from clarification)
- **Mode case**: Case-insensitive - accept 'overwrite', 'OVERWRITE', 'Overwrite' etc.
- **Batch update**: Single object only - each update call handles one object ID
- **Nested fields**: Use dot notation - `--solution.cot`, `--proof.cot` for intuitive mapping

### Step 1: Update `src/utils.py` - Add update functionality

#### 1.1 Add helper function to get object type from ID
```python
def get_object_type_from_id(obj_id: str) -> str:
    """Extract object type from ID prefix.

    Args:
        obj_id: Object ID (e.g., "s-001", "p-001")

    Returns:
        Object type: "p", "s", or "e"
    """
    return obj_id.split("-")[0]
```

#### 1.2 Add helper function to load an object
```python
def load_object(obj_id: str) -> dict:
    """Load an object from file by ID.

    Args:
        obj_id: Object ID (e.g., "s-001", "p-001")

    Returns:
        Object data as dict

    Raises:
        FileNotFoundError: If object file doesn't exist
    """
```

#### 1.3 Add helper function to apply updates with mode handling
```python
def apply_updates(obj_data: dict, updates: dict[str, Any]) -> dict:
    """Apply updates to an object, handling nested fields and list modes.

    Args:
        obj_data: Current object data
        updates: Dict of field paths to new values
                 For list fields: value is tuple (mode, values)
                 For single fields: value is the new value

    Returns:
        Updated object data

    Supports dot notation for nested fields:
        - "solution.cot" -> obj_data["solution"]["cot"]
        - "proof.full" -> obj_data["proof"]["full"]
    """
```

#### 1.4 Add `update_objects()` function to LogManager or as standalone
```python
def update_objects(updates_list: list[tuple[str, dict]]) -> tuple[str, list[str]]:
    """Update objects and log the changes with version backup.

    IMPORTANT: This is the ONLY function that should modify existing object files.

    Args:
        updates_list: List of (obj_id, updates_dict) tuples
                      updates_dict maps field paths to new values

    Returns:
        Tuple of (log_id, list of modified object IDs)

    Process:
        1. Generate log_id
        2. Create backup folder: contents/history/{log_id}/
        3. For each object:
           a. Load current object
           b. Copy to backup folder
           c. Apply updates
           d. Write updated object back
        4. Write log entry with "current" field containing [p, s, e] indices
    """
```

#### 1.5 Add HISTORY_FOLDER constant
```python
HISTORY_FOLDER = os.path.join(PROJECT_ROOT, "contents/history")
```

### Step 2: Create `src/state_update.py`

#### 2.1 File structure
```python
import argparse
from utils import load_object, update_objects

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
```

#### 2.2 CLI argument parsing in main block
```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update a statement")

    # Required
    parser.add_argument('--id', type=str, required=True, help='Statement ID to update')

    # Single-value params
    parser.add_argument('--status', type=str, help='New status value')
    parser.add_argument('--proof.full', type=str, dest='proof_full', help='Full proof text')

    # Multiple-value params (mode + values)
    parser.add_argument('--dependencies', nargs='+', type=str,
                        help='Mode (Overwrite/Append) followed by values')
    parser.add_argument('--proof.cot', nargs='+', type=str, dest='proof_cot',
                        help='Mode (Overwrite/Append) followed by chain-of-thought steps')
```

#### 2.3 Parse and build updates dict
```python
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
        mode = args.dependencies[0].lower()  # Case-insensitive
        values = args.dependencies[1:]
        updates["dependencies"] = (mode, values)
    if args.proof_cot:
        mode = args.proof_cot[0].lower()
        values = args.proof_cot[1:]
        updates["proof.cot"] = (mode, values)

    return updates
```

### Step 3: Create `src/prob_update.py`

#### 3.1 File structure (similar to state_update.py)
```python
import argparse
from utils import load_object, update_objects

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
```

#### 3.2 CLI argument parsing in main block
```python
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
```

### Step 4: History Backup Structure

When updating objects, the backup folder structure will be:
```
contents/
└── history/
    ├── log.jsonl              # Log entries with "current" field
    ├── l-002/                  # Backup folder for log l-002
    │   ├── s-001.json         # Old version of s-001 before update
    │   └── p-001.json         # Old version of p-001 before update
    └── l-003/
        └── s-005.json
```

**Log entry format:**
```json
{"l-002": {"creation": [], "modification": ["s-001"]}, "current": ["p-001", "s-013", "e-000"]}
```
- The `"current"` field tracks the indices after the operation (p, s, e only - no log index)

### File Changes Summary

| File | Changes |
|------|---------|
| `src/utils.py` | Add `HISTORY_FOLDER`, `get_object_type_from_id()`, `load_object()`, `apply_updates()`, `update_objects()` |
| `src/state_update.py` | Create new file with `update_statement()` function and CLI argument parsing |
| `src/prob_update.py` | Create new file with `update_problem()` function and CLI argument parsing |

### CLI Usage Examples

**Update statement status:**
```bash
python state_update.py --id s-001 --status true
```

**Update statement with proof:**
```bash
python state_update.py --id s-001 --status true --proof.full "Proven by direct calculation"
```

**Append to dependencies:**
```bash
python state_update.py --id s-005 --dependencies Append s-001 s-002
```

**Overwrite proof chain-of-thought:**
```bash
python state_update.py --id s-001 --proof.cot Overwrite "Step 1: ..." "Step 2: ..."
```

**Update problem with multiple fields:**
```bash
python prob_update.py --id p-001 --status resolved --solution.full "Answer is 8"
```

**Append preliminary steps:**
```bash
python prob_update.py --id p-001 --preliminary Append "First, note that..."
```

### Test Plan
1. Create a test problem and statements using `prob_init.py`
2. Update a single field on a statement (e.g., status)
3. Verify:
   - Object file updated correctly
   - Backup created in `contents/history/l-XXX/`
   - Log entry added to `log.jsonl` with modification list
4. Test append mode on a list field
5. Test overwrite mode on a list field
6. Test nested field update (e.g., proof.cot)
7. Test updating multiple fields in one call