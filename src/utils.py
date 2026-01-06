import json
import os


CONFIG_PATH = "contents/config.json"

VALID_TYPES = ["p", "s", "e"]


def ensure_config() -> dict:
    """Ensure config file exists and return its contents."""
    os.makedirs("contents", exist_ok=True)

    if not os.path.exists(CONFIG_PATH):
        config = {
            "p": "p-000",
            "s": "s-000",
            "e": "e-000"
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
            "p": config["p"],
            "s": config["s"],
            "e": config["e"]
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
            type: One of "p" (problem), "s" (statement), "e" (experience)

        Returns:
            The new ID string (e.g., "p-003", "s-a001")

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
