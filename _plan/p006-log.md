# Develop a log system

## Meta Info
- **Script** `src/utils.py` (modify)
- **Log save_path** `contents/history/log.jsonl`
- **Current scripts involving changes** `src/prob_init.py` (`create_problem()`) and `src/state_init.py` (`create_statement()`)

## Instruction
1. Add a new log Manager, to log any changes.
- Changes are to be logged when:
    - A new object (problem, statement, experience) is to be added. <- We haven't implement the experience system yet. Now only handle problem and statement.
    - An existing object to be modified. <- We haven't implement update yet. Now can only handle new object creation.
- Change type: either creation or modification.
    - For creation, only need to record the id.
    - For modification, need to record the full old object.
- Nested cases: if a change on one object involves multiple subsequent changes of other objects (for example, creating a new problem involving creating a few statements as hypothesis), all the changes will be logged with a single id.

2. Update the Id Manager:
- In `contents/config.json`, add a new key `l` for logs. Adopting the same indexing logic as others.
- Each time a change is to be made, create a new id for logs.

3. Unify the current scripts:
- Currently the changes are implemented in each individual functions, which is hard to maintain.
- Create a unified creation function for creating all types of objects. It handles the following:
    - It receives a full list of object creation.
    - When creating objects, it handles the log id management as well.
    - It creates not only the objects, but also the logs at the same time.
**Note** At this stage, we only need to handle new object creation.
- Modify the current functions `create_problem()` and `create_statement()`:
    - Add a new param `root_change: bool = true`. This handles nested creation.
        - When `create_problem()` calls `create_statement()`, set `root_change = false`.
        - The two functions `create_problem()` and `create_statement()` first compose a list of objects to be created.
        - If `root_change == true`, we call corresponding method from log manager to update.
        - If `root_change == false` (in nested case), we simply return the list of objects to be created for the root-changer to handle.
**Note** At initial problem creation, our current modification is to modify the status of each statement to be "true". Please implement this in the flow to compose the list of objects to create: we modify the items in this list instead of first creating them and modify. Thus these objects are "born with status = true."

4. Log format
```json
{
    "{{log_id}}": {
        "creation": [
            "list of object ids that are created for this change"
        ],
        "modification": [
            "list of object ids that are modified for this change"
        ]
    }
}
```

## Test
- I have cleaned the past test data.
- Simply use `puzzle_test.md` to test the new system. (You need to parse the hypothesis.)

---

## Implementation Plan

### Design Decisions (from clarification)
- **Log format**: JSONL - each log entry is a separate JSON line
- **Unified creation**: The unified function handles everything (object preparation, file writing, log creation)
- **Return type**: When `root_change=false`, return full object data as `list[(object_type, object_data)]` tuples

### Step 1: Update `src/utils.py` - Extend IDManager and add LogManager

#### 1.1 Update VALID_TYPES and ensure_config()
```python
VALID_TYPES = ["p", "s", "e", "l"]  # Add "l" for logs
```

Update `ensure_config()` to include `"l": "l-000"` in the default config.

#### 1.2 Update IDManager.__init__()
Add `"l"` to `_current_ids` initialization to handle log IDs.

#### 1.3 Add LogManager class

**Design Principle**: All change operations (both creation and modification) MUST be handled through this manager. This ensures that the log step and the actual change step are always executed together atomically, preventing chaos in history management. Never write objects directly to files outside of this manager.

```python
class LogManager:
    """Singleton manager for logging changes to objects.

    IMPORTANT: All change operations (creation/modification) should be routed
    through this manager. This ensures that:
    1. The log entry and the actual file changes are always in sync
    2. History is never corrupted by partial operations
    3. There is a single source of truth for all mutations

    Usage pattern:
    - Do NOT write object files directly in create_xxx() functions
    - Instead, collect objects to create, then call commit_objects()
    - commit_objects() handles both file writing AND log creation atomically
    """
    _instance = None
    _initialized = False

    LOG_PATH = "contents/history/log.jsonl"

    def __new__(cls): ...
    def __init__(self): ...

    def log_changes(self, created_ids: list[str], modified_ids: list[str] = None) -> str:
        """
        Log a batch of changes (creations and modifications).

        Args:
            created_ids: List of object IDs that were created
            modified_ids: List of object IDs that were modified (with old data)

        Returns:
            The log ID for this change batch
        """
        # Generate log ID
        # Write log entry as JSONL line
        # Return log_id
```

#### 1.4 Add unified creation function
```python
def commit_objects(objects: list[tuple[str, dict]]) -> tuple[str, list[str]]:
    """
    Unified function to create objects and log the changes.

    Args:
        objects: List of (object_type, object_data) tuples
                 object_type is one of "p", "s", "e"
                 object_data is the full object dict (with id already assigned)

    Returns:
        Tuple of (log_id, list of created object IDs)

    Behavior:
        1. Write each object to its corresponding file
        2. Create a log entry with all created IDs
        3. Return the log_id and list of created IDs
    """
```

Helper mapping for file paths:
```python
OBJECT_FOLDERS = {
    "p": "contents/problem",
    "s": "contents/statement",
    "e": "contents/experience"
}
```

### Step 2: Update `src/state_init.py` - Modify create_statement()

#### 2.1 Update function signature
```python
def create_statement(
    type: str,
    conclusion: list[str],
    hypothesis: list[str] | None = None,
    root_change: bool = True,      # NEW
    status: str = "pending"        # NEW: allow setting initial status
) -> str | tuple[str, dict]:
```

#### 2.2 Update function logic
```python
def create_statement(...):
    # Validate type
    # Generate ID
    # Build statement object (using provided status instead of default)

    if root_change:
        # Call commit_objects() to write file and create log
        # Return statement_id
    else:
        # Return (object_type, object_data) tuple for parent to handle
        return ("s", asdict(statement))
```

### Step 3: Update `src/prob_init.py` - Modify create_problem()

#### 3.1 Update function signature
```python
def create_problem(
    hypothesis: list[str],
    objectives: list[str],
    initial: bool = False,
    root_change: bool = True       # NEW
) -> str | tuple[str, list[tuple[str, dict]]]:
```

#### 3.2 Update process_hypothesis_item()
Modify to accept and pass `root_change=False` to `create_statement()`, and collect returned objects:

```python
def process_hypothesis_item(item: str, initial: bool) -> tuple[str, list[tuple[str, dict]]]:
    """
    Process single hypothesis item.

    Returns:
        Tuple of (formatted_hypothesis_string, list of objects to create)
    """
    # ... existing logic ...

    if need_new_statement:
        statement_type = "assumption" if initial else "normal"
        # Set status='true' if initial, else 'pending'
        status = "true" if initial else "pending"

        obj_type, obj_data = create_statement(
            type=statement_type,
            conclusion=[cleaned_text],
            hypothesis=None,
            root_change=False,       # Nested call
            status=status            # Born with correct status
        )
        return (f"({obj_data['id']}) {cleaned_text}", [(obj_type, obj_data)])

    return (formatted_string, [])
```

#### 3.3 Update create_problem() main logic
```python
def create_problem(...):
    # Collect all objects to be created
    objects_to_create = []
    processed_hypothesis = []

    for item in hypothesis:
        formatted, new_objects = process_hypothesis_item(item, initial)
        processed_hypothesis.append(formatted)
        objects_to_create.extend(new_objects)

    # Generate problem ID and build problem object
    problem_id = id_manager.generate_id("p")
    problem = type_problem(...)
    objects_to_create.append(("p", asdict(problem)))

    if root_change:
        # Commit all objects and create log
        log_id, created_ids = commit_objects(objects_to_create)
        return problem_id
    else:
        # Return all objects for parent to handle
        return (problem_id, objects_to_create)
```

#### 3.4 Remove set_statement_status_true()
This function is no longer needed since statements will be "born with status=true" when `initial=True`.

### Step 4: Create log directory structure

Ensure `contents/history/` directory exists. This can be handled in `LogManager.__init__()` or `commit_objects()`.

### File Changes Summary

| File | Changes |
|------|---------|
| `src/utils.py` | Add `"l"` to VALID_TYPES, update `ensure_config()`, update `IDManager`, add `LogManager` class, add `commit_objects()` function |
| `src/state_init.py` | Add `root_change` and `status` params to `create_statement()`, update return logic |
| `src/prob_init.py` | Add `root_change` param to `create_problem()`, update `process_hypothesis_item()` return type, remove `set_statement_status_true()`, refactor to collect objects then commit |
| `contents/config.json` | Will be auto-updated by `ensure_config()` to add `"l": "l-000"` |

### Test Plan
1. Delete any existing test data in `contents/problem/`, `contents/statement/`, `contents/history/`
2. Parse `puzzle_test.md` to extract hypothesis (e.g., "I have three apples", "my sister has two more apples than I")
3. Call `create_problem()` with `initial=True`
4. Verify:
   - Problem JSON created in `contents/problem/`
   - Statement JSONs created in `contents/statement/` with `status="true"`
   - Log entry created in `contents/history/log.jsonl`
   - `contents/config.json` updated with new IDs for p, s, and l
