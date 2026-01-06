# Develop rewind functionality
Develop a rewind functionality based on the history.

## Meta Info
- **Script:** `src/rewind.py` (create)

**Special Note**
- This script is NOT designed for agent to use. Its solo purpose is to support user's developmenet of the whole workflow.

## Instruction
1. Main block
- A varaible "targeted_log_id: str"
- No terminal argument realization for this script.

2. Input validation
Check if the variable takes a reasonable value, i.e., a line in `contents/history/log.jsonl` has this key.

3. Rewind method
- Read the `current` value from the found line from `contents/history/log.jsonl`. It contains info to update the file `contents/config.json`.
- Remove any newer objects.
- Rewind old objects that get changed:
    - Enumerate lines in `contents/history/log.jsonl`, and find the first time after the target_log_id when an object get updated. Read the log_id of this line, the folder `contents/history/{{log_id}}` contains the old version of the object before the change. This is supposed to be object status at the targeted_log_id.
    - Edge case: when an object is modified at target_log_id: we are expected to rewind to the moment change at target_log_id is finished. So no need to take special care for objects changed at target_log_id. Only replace old objects that are updated (strictly) after target_log_id.
- Only find the first time an object get updated: an object might get updated several times. Only the first (after targeted_log_id) among all updates is relevant to the status at the targeted_log_id.

**Note**
- We only need to transverse `contents/history/log.jsonl` once, since it is logged in the natural order:
    - If no targeted_log_id found, validation failed.
    - When targeted_log_id is found, update `contents/config.json`.
    - After passing targeted_log_id, start to rewind objects.
    - Can create a set of already_rewinded_objects to skip multi-updated objects.

## Safety lock
- To avoid agents accidentally use this script to rewind (as rewind is designed to be non-reversable), add a confirmation in terminal: user need to input "y" to confirm rewind. Thus, the agent will not be able to use bash command to start a rewind.
- Also add a special comment to the script around this safety lock. Make it very clear that any edits is not supposed to remove it.

## Test
- Can test the on the current setup (have up to l-004).

---

## Implementation Plan

### Design Decisions (from clarification)
- **Log cleanup**: Remove newer log entries - truncate log.jsonl to remove all entries after targeted_log_id
- **Backup cleanup**: Delete backup folders for log entries newer than targeted_log_id

### Clarifications
1. **Default value for targeted_log_id**: Set to `None` by default. If user runs without setting it, report an error.
2. **Development workflow**:
   - Implement all functionalities (without safety lock)
   - Test on current contents
   - Reset `targeted_log_id` to `None`
   - Add safety lock (confirmation in terminal)

### Step 1: Create `src/rewind.py` - File structure

```python
import json
import os
import shutil

from utils import PROJECT_ROOT, OBJECT_FOLDERS, HISTORY_FOLDER, CONFIG_PATH

LOG_PATH = os.path.join(HISTORY_FOLDER, "log.jsonl")
```

### Step 2: Input validation

```python
def validate_log_id(log_id: str | None) -> bool:
    """Check if log_id is set and exists in log.jsonl.

    Args:
        log_id: The log ID to validate (e.g., "l-002"), or None if not set

    Returns:
        True if log_id exists, False otherwise
    """
    # Check if log_id is set
    if log_id is None:
        print("Error: targeted_log_id is not set.")
        print("Please set targeted_log_id to a valid log ID (e.g., 'l-002') before running.")
        return False

    with open(LOG_PATH, "r") as f:
        for line in f:
            entry = json.loads(line.strip())
            if log_id in entry:
                return True
    return False
```

### Step 3: Main rewind logic

#### 3.1 Parse log.jsonl in single traversal

```python
def rewind_to(log_id: str) -> None:
    """Rewind the system state to the specified log_id.

    Process (single traversal of log.jsonl):
    1. Find targeted_log_id line, extract "current" for config update
    2. Track all objects created after targeted_log_id (to delete)
    3. Track first modification of each object after targeted_log_id (to restore)
    4. Track log_ids after targeted_log_id (for backup folder cleanup)
    """
```

#### 3.2 State tracking variables

```python
# State variables during traversal
found_target = False
target_current = None  # [p-XXX, s-XXX, e-XXX] from target line
objects_to_delete = []  # Objects created after target
objects_to_restore = {}  # {obj_id: first_log_id_after_target_that_modified_it}
already_tracked = set()  # Objects already tracked for restore (skip duplicates)
logs_to_cleanup = []  # Log IDs after target (for backup folder deletion)
```

#### 3.3 Traversal logic

```python
with open(LOG_PATH, "r") as f:
    for line in f:
        entry = json.loads(line.strip())

        # Extract log_id (first key that starts with "l-")
        current_log_id = None
        for key in entry:
            if key.startswith("l-"):
                current_log_id = key
                break

        if not found_target:
            if current_log_id == log_id:
                found_target = True
                target_current = entry["current"]
        else:
            # After target: collect cleanup info
            logs_to_cleanup.append(current_log_id)

            # Track objects created after target (to delete)
            created = entry[current_log_id].get("creation", [])
            objects_to_delete.extend(created)

            # Track first modification of objects after target (to restore)
            modified = entry[current_log_id].get("modification", [])
            for obj_id in modified:
                if obj_id not in already_tracked:
                    objects_to_restore[obj_id] = current_log_id
                    already_tracked.add(obj_id)
```

### Step 4: Execute rewind operations

#### 4.1 Update config.json

```python
def update_config(current: list[str], log_id: str) -> None:
    """Update config.json with rewound state.

    Args:
        current: [p-XXX, s-XXX, e-XXX] from target log entry
        log_id: The target log_id (for setting "l" value)
    """
    config = {
        "p": current[0],
        "s": current[1],
        "e": current[2],
        "l": log_id
    }
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)
```

#### 4.2 Delete newer objects

```python
def delete_objects(obj_ids: list[str]) -> None:
    """Delete object files created after target.

    Args:
        obj_ids: List of object IDs to delete
    """
    for obj_id in obj_ids:
        obj_type = obj_id.split("-")[0]
        if obj_type in OBJECT_FOLDERS:
            file_path = os.path.join(OBJECT_FOLDERS[obj_type], f"{obj_id}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"  Deleted: {file_path}")
```

#### 4.3 Restore modified objects

```python
def restore_objects(restore_map: dict[str, str]) -> None:
    """Restore objects to their state at target log_id.

    Args:
        restore_map: {obj_id: log_id_with_backup}
                     The backup folder contents/history/{log_id}/ contains
                     the old version BEFORE the modification at that log_id,
                     which is the state at target_log_id.
    """
    for obj_id, backup_log_id in restore_map.items():
        obj_type = obj_id.split("-")[0]
        if obj_type in OBJECT_FOLDERS:
            backup_path = os.path.join(HISTORY_FOLDER, backup_log_id, f"{obj_id}.json")
            target_path = os.path.join(OBJECT_FOLDERS[obj_type], f"{obj_id}.json")

            if os.path.exists(backup_path):
                shutil.copy2(backup_path, target_path)
                print(f"  Restored: {obj_id} from {backup_log_id}")
```

#### 4.4 Cleanup log.jsonl and backup folders

```python
def cleanup_history(target_log_id: str, logs_to_remove: list[str]) -> None:
    """Remove log entries after target and delete backup folders.

    Args:
        target_log_id: The target log ID (keep this and earlier)
        logs_to_remove: List of log IDs to remove
    """
    # Truncate log.jsonl: keep only lines up to and including target
    lines_to_keep = []
    with open(LOG_PATH, "r") as f:
        for line in f:
            lines_to_keep.append(line)
            entry = json.loads(line.strip())
            if target_log_id in entry:
                break

    with open(LOG_PATH, "w") as f:
        f.writelines(lines_to_keep)
    print(f"  Truncated log.jsonl (kept up to {target_log_id})")

    # Delete backup folders
    for log_id in logs_to_remove:
        folder_path = os.path.join(HISTORY_FOLDER, log_id)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            print(f"  Deleted backup folder: {folder_path}")
```

### Step 5: Safety lock implementation

```python
# ============================================================================
# SAFETY LOCK - DO NOT REMOVE OR MODIFY THIS SECTION
# This confirmation prevents agents from accidentally triggering rewind.
# Rewind is a DESTRUCTIVE, NON-REVERSIBLE operation.
# ============================================================================
def confirm_rewind() -> bool:
    """Require user confirmation before proceeding with rewind.

    Returns:
        True if user confirms with 'y', False otherwise
    """
    print("\n" + "=" * 60)
    print("WARNING: REWIND IS A NON-REVERSIBLE OPERATION")
    print("=" * 60)
    print(f"You are about to rewind to: {targeted_log_id}")
    print("This will:")
    print("  - Delete all objects created after this point")
    print("  - Restore modified objects to their previous state")
    print("  - Remove log entries after this point")
    print("  - Delete backup folders after this point")
    print("=" * 60)

    response = input("Type 'y' to confirm rewind: ")
    return response.strip().lower() == 'y'
# ============================================================================
# END SAFETY LOCK
# ============================================================================
```

### Step 6: Main block

```python
if __name__ == "__main__":
    # =========================================================
    # USER: Set the target log ID here before running
    # =========================================================
    targeted_log_id = None  # <-- Change this to a valid log ID (e.g., "l-002")
    # =========================================================

    # Validate target (handles None check and existence check)
    if not validate_log_id(targeted_log_id):
        if targeted_log_id is not None:
            print(f"Error: Log ID '{targeted_log_id}' not found in log.jsonl")
        exit(1)

    # Safety confirmation (added after testing)
    if not confirm_rewind():
        print("Rewind cancelled.")
        exit(0)

    # Execute rewind
    print(f"\nRewinding to {targeted_log_id}...")
    rewind_to(targeted_log_id)
    print("\nRewind complete.")
```

### File Structure Summary

```
src/rewind.py
├── Imports and constants (LOG_PATH)
├── validate_log_id()
├── update_config()
├── delete_objects()
├── restore_objects()
├── cleanup_history()
├── rewind_to() - main orchestrator
├── confirm_rewind() - SAFETY LOCK
└── if __name__ == "__main__": block
    └── targeted_log_id = None  # <-- User sets this value here
```

### Development Workflow

1. **Implement without safety lock**: Create the script with all functionality but comment out or skip the safety confirmation
2. **Test on current setup** (l-001 to l-004):
   - Test rewind to l-003 (restores s-014 to pre-update state)
   - Verify results
3. **Reset targeted_log_id**: Set back to `None`
4. **Add safety lock**: Uncomment/enable the confirmation prompt

### Test Plan

Using current setup (l-001 to l-004):

1. **Test rewind to l-003** (recommended first test - only restores, no deletes):
   - Should delete: nothing (no creations after l-003)
   - Should restore: s-014 to its state before l-004 modification (status="pending", proof.full="")
   - Config should become: `{"p": "p-002", "s": "s-014", "e": "e-000", "l": "l-003"}`
   - Log.jsonl truncated to 3 lines
   - Backup folder l-004 deleted

2. **Test rewind to l-002**:
   - Should delete: s-014 (created in l-003)
   - Should restore: nothing (s-014 was created after l-002, so deleted not restored)
   - Config should become: `{"p": "p-002", "s": "s-013", "e": "e-000", "l": "l-002"}`

3. **Test rewind to l-001**:
   - Should delete: p-002, s-014
   - Should restore: nothing
   - Config should become: `{"p": "p-001", "s": "s-013", "e": "e-000", "l": "l-001"}`
