import json
import os
import shutil

from utils import OBJECT_FOLDERS, HISTORY_FOLDER, CONFIG_PATH

LOG_PATH = os.path.join(HISTORY_FOLDER, "log.jsonl")


def validate_log_id(log_id: str | None) -> bool:
    """Check if log_id is set and exists in log.jsonl.

    Args:
        log_id: The log ID to validate (e.g., "l-002"), or None if not set

    Returns:
        True if log_id exists or is "l-000" (special reset case), False otherwise
    """
    # Check if log_id is set
    if log_id is None:
        print("Error: targeted_log_id is not set.")
        print("Please set targeted_log_id to a valid log ID (e.g., 'l-002') before running.")
        return False

    # Special case: l-000 is always valid (reset to initial state)
    if log_id == "l-000":
        return True

    with open(LOG_PATH, "r") as f:
        for line in f:
            entry = json.loads(line.strip())
            if log_id in entry:
                return True
    return False


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
    print(f"  Updated config.json")


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
                print(f"  Deleted: {obj_id}")


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
            print(f"  Deleted backup folder: {log_id}")


# ============================================================================
# SAFETY LOCK - DO NOT REMOVE OR MODIFY THIS SECTION
# This confirmation prevents agents from accidentally triggering rewind.
# Rewind is a DESTRUCTIVE, NON-REVERSIBLE operation.
# ============================================================================
def confirm_rewind(log_id: str) -> bool:
    """Require user confirmation before proceeding with rewind.

    Returns:
        True if user confirms with 'y', False otherwise
    """
    print("\n" + "=" * 60)
    print("WARNING: REWIND IS A NON-REVERSIBLE OPERATION")
    print("=" * 60)
    print(f"You are about to rewind to: {log_id}")

    if log_id == "l-000":
        print("\n*** FULL RESET TO INITIAL STATE ***")
        print("This will:")
        print("  - DELETE ALL objects (problems, statements, experiences)")
        print("  - CLEAR the entire log history")
        print("  - DELETE ALL backup folders")
        print("  - RESET all IDs to '-000'")
    else:
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


def reset_to_initial() -> None:
    """Reset the system to initial state (l-000).

    This is a special case that:
    1. Deletes ALL objects in problem, statement, experience folders
    2. Clears log.jsonl (empty file)
    3. Deletes ALL backup folders in history
    4. Resets config.json to initial state (all IDs to "-000")
    """
    print("\n[1/4] Resetting config.json to initial state...")
    config = {
        "p": "p-000",
        "s": "s-000",
        "e": "e-000",
        "l": "l-000"
    }
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)
    print("  Reset config.json")

    print("\n[2/4] Deleting all objects...")
    for folder in OBJECT_FOLDERS.values():
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                if filename.endswith(".json"):
                    file_path = os.path.join(folder, filename)
                    os.remove(file_path)
                    print(f"  Deleted: {filename}")

    print("\n[3/4] Clearing log.jsonl...")
    with open(LOG_PATH, "w") as f:
        pass  # Empty the file
    print("  Cleared log.jsonl")

    print("\n[4/4] Deleting all backup folders...")
    if os.path.exists(HISTORY_FOLDER):
        for item in os.listdir(HISTORY_FOLDER):
            item_path = os.path.join(HISTORY_FOLDER, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"  Deleted backup folder: {item}")


def rewind_to(log_id: str) -> None:
    """Rewind the system state to the specified log_id.

    Process (single traversal of log.jsonl):
    1. Find targeted_log_id line, extract "current" for config update
    2. Track all objects created after targeted_log_id (to delete)
    3. Track first modification of each object after targeted_log_id (to restore)
    4. Track log_ids after targeted_log_id (for backup folder cleanup)
    """
    # State variables during traversal
    found_target = False
    target_current = None  # [p-XXX, s-XXX, e-XXX] from target line
    objects_to_delete = []  # Objects created after target
    objects_to_restore = {}  # {obj_id: first_log_id_after_target_that_modified_it}
    already_tracked = set()  # Objects already tracked for restore (skip duplicates)
    logs_to_cleanup = []  # Log IDs after target (for backup folder deletion)

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

    # Execute rewind operations
    print("\n[1/4] Updating config.json...")
    update_config(target_current, log_id)

    print("\n[2/4] Deleting objects created after target...")
    if objects_to_delete:
        delete_objects(objects_to_delete)
    else:
        print("  No objects to delete")

    print("\n[3/4] Restoring modified objects...")
    if objects_to_restore:
        restore_objects(objects_to_restore)
    else:
        print("  No objects to restore")

    print("\n[4/4] Cleaning up history...")
    cleanup_history(log_id, logs_to_cleanup)


if __name__ == "__main__":
    # =========================================================
    # USER: Set the target log ID here before running
    # =========================================================
    targeted_log_id = "l-000"  # <-- Change this to a valid log ID (e.g., "l-002")
    # =========================================================

    # Validate target (handles None check and existence check)
    if not validate_log_id(targeted_log_id):
        if targeted_log_id is not None:
            print(f"Error: Log ID '{targeted_log_id}' not found in log.jsonl")
        exit(1)

    # Safety confirmation
    if not confirm_rewind(targeted_log_id):
        print("Rewind cancelled.")
        exit(0)

    # Execute rewind
    print(f"\nRewinding to {targeted_log_id}...")
    if targeted_log_id == "l-000":
        reset_to_initial()
    else:
        rewind_to(targeted_log_id)
    print("\nRewind complete.")
