import json
import os


# Get project root (parent of src folder)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG_PATH = os.path.join(PROJECT_ROOT, "contents/config.json")

VALID_TYPES = ["p", "s", "e", "l"]

OBJECT_FOLDERS = {
    "p": os.path.join(PROJECT_ROOT, "contents/problem"),
    "s": os.path.join(PROJECT_ROOT, "contents/statement"),
    "e": os.path.join(PROJECT_ROOT, "contents/experience")
}


def ensure_config() -> dict:
    """Ensure config file exists and return its contents."""
    os.makedirs(os.path.join(PROJECT_ROOT, "contents"), exist_ok=True)

    if not os.path.exists(CONFIG_PATH):
        config = {
            "p": "p-000",
            "s": "s-000",
            "e": "e-000",
            "l": "l-000"
        }
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=4)
    else:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)

    return config


def increment_letters(letters: str) -> str:
    """Increment letter sequence like base-26.

    Examples:
        "" -> "a"
        "a" -> "b"
        "z" -> "aa"
        "az" -> "ba"
        "zz" -> "aaa"
    """
    if not letters:
        return "a"

    # Convert to list for easier manipulation
    chars = list(letters)

    # Increment from right to left (like adding 1 to a number)
    i = len(chars) - 1
    while i >= 0:
        if chars[i] == 'z':
            chars[i] = 'a'
            i -= 1
        else:
            chars[i] = chr(ord(chars[i]) + 1)
            return ''.join(chars)

    # All were 'z', need to add a new 'a' at the front
    return 'a' + ''.join(chars)


def increment_id(current_id: str) -> str:
    """Parse and increment the counter part of an ID.

    Examples:
        "p-000" -> "p-001"
        "p-999" -> "p-a001"
        "p-a999" -> "p-b001"
        "p-z999" -> "p-aa001"
    """
    # Split by '-' to get prefix and counter
    parts = current_id.split('-')
    prefix = parts[0]
    counter = parts[1]

    # Parse counter into letter part and number part
    letters = ""
    num_str = counter

    # Extract leading letters
    i = 0
    while i < len(counter) and counter[i].isalpha():
        letters += counter[i]
        i += 1
    num_str = counter[i:]

    # Parse number
    number = int(num_str) if num_str else 0

    # Increment logic
    if number < 999:
        number += 1
    else:
        # Number is 999, need to increment letters and reset number
        letters = increment_letters(letters)
        number = 1

    # Return formatted ID
    return f"{prefix}-{letters}{number:03d}"


class IDManager:
    """Singleton manager for ID generation and tracking.

    This class ensures a single source of truth for ID management across
    the application. Config file is read once at initialization and updated
    atomically on each ID generation.
    """
    _instance = None
    _initialized = False

    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the IDManager (only once)."""
        if IDManager._initialized:
            return

        # Read config once at initialization
        config = ensure_config()

        # Store current IDs as dict for direct access
        self._current_ids = {
            "p": config.get("p", "p-000"),
            "s": config.get("s", "s-000"),
            "e": config.get("e", "e-000"),
            "l": config.get("l", "l-000")
        }

        # Store config path for updates
        self._config_path = CONFIG_PATH

        IDManager._initialized = True

    @property
    def current_ids(self) -> dict[str, str]:
        """Return a copy of current IDs for read-only access.

        Returns:
            Dict of current IDs: {"p": "p-003", "s": "s-017", "e": "e-000"}
        """
        return self._current_ids.copy()

    def generate_id(self, type: str) -> str:
        """Generate a new ID, update instance state, and persist to config.

        Args:
            type: One of "p" (problem), "s" (statement), "e" (experience), "l" (log)

        Returns:
            The new ID string (e.g., "p-003", "s-a001", "l-001")

        Raises:
            ValueError: If type is not valid
        """
        if type not in VALID_TYPES:
            raise ValueError(f"Invalid type '{type}'. Expected one of: {VALID_TYPES}")

        # Get current ID and generate new one
        current_id = self._current_ids[type]
        new_id = increment_id(current_id)

        # Update instance variable
        self._current_ids[type] = new_id

        # Persist to config.json
        with open(self._config_path, "w") as f:
            json.dump(self._current_ids, f, indent=4)

        return new_id


def id_generation(type: str) -> str:
    """Legacy function for backward compatibility.

    Args:
        type: One of "p" (problem), "s" (statement), "e" (experience)

    Returns:
        The new ID string (e.g., "p-003", "s-a001")
    """
    return IDManager().generate_id(type)


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

    LOG_PATH = os.path.join(PROJECT_ROOT, "contents/history/log.jsonl")

    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the LogManager (only once)."""
        if LogManager._initialized:
            return

        # Ensure log directory exists
        os.makedirs(os.path.dirname(self.LOG_PATH), exist_ok=True)

        LogManager._initialized = True

    def log_changes(
        self,
        created_ids: list[str],
        modified_ids: list[str] | None = None
    ) -> str:
        """Log a batch of changes (creations and modifications).

        Args:
            created_ids: List of object IDs that were created
            modified_ids: List of object IDs that were modified

        Returns:
            The log ID for this change batch
        """
        # Generate log ID
        id_manager = IDManager()
        log_id = id_manager.generate_id("l")

        # Build log entry
        log_entry = {
            log_id: {
                "creation": created_ids,
                "modification": modified_ids if modified_ids else []
            }
        }

        # Append to JSONL file
        with open(self.LOG_PATH, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        return log_id


def commit_objects(objects: list[tuple[str, dict]]) -> tuple[str, list[str]]:
    """Unified function to create objects and log the changes.

    IMPORTANT: This is the ONLY function that should write object files.
    All create_xxx() functions should collect objects and delegate to this
    function to ensure log and file changes are always in sync.

    Args:
        objects: List of (object_type, object_data) tuples
                 object_type is one of "p", "s", "e"
                 object_data is the full object dict (with id already assigned)

    Returns:
        Tuple of (log_id, list of created object IDs)
    """
    if not objects:
        raise ValueError("Cannot commit empty object list")

    created_ids = []

    # Write each object to its corresponding file
    for obj_type, obj_data in objects:
        if obj_type not in OBJECT_FOLDERS:
            raise ValueError(f"Invalid object type '{obj_type}'. Expected one of: {list(OBJECT_FOLDERS.keys())}")

        folder = OBJECT_FOLDERS[obj_type]
        os.makedirs(folder, exist_ok=True)

        obj_id = obj_data["id"]
        file_path = os.path.join(folder, f"{obj_id}.json")

        with open(file_path, "w") as f:
            json.dump(obj_data, f, indent=4)

        created_ids.append(obj_id)

    # Create log entry
    log_manager = LogManager()
    log_id = log_manager.log_changes(created_ids=created_ids)

    return log_id, created_ids
