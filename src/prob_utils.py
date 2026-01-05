import json
import os


CONFIG_PATH = "contents/config.json"

TYPE_MAP = {
    "p": "count_problems",
    "s": "count_statements",
    "e": "count_experiences"
}


def ensure_config() -> dict:
    """Ensure config file exists and return its contents.

    Handles migration from integer format to string format.
    """
    os.makedirs("contents", exist_ok=True)

    if not os.path.exists(CONFIG_PATH):
        config = {
            "count_problems": "p-000",
            "count_statements": "s-000",
            "count_experiences": "e-000"
        }
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=4)
    else:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)

        # Migrate from integer format to string format if needed
        needs_migration = False
        if isinstance(config.get("count_problems"), int):
            count = config["count_problems"]
            config["count_problems"] = f"p-{count:03d}" if count > 0 else "p-000"
            needs_migration = True
        if isinstance(config.get("count_statements"), int):
            count = config["count_statements"]
            config["count_statements"] = f"s-{count:03d}" if count > 0 else "s-000"
            needs_migration = True
        if isinstance(config.get("count_experiences"), int):
            count = config["count_experiences"]
            config["count_experiences"] = f"e-{count:03d}" if count > 0 else "e-000"
            needs_migration = True

        if needs_migration:
            with open(CONFIG_PATH, "w") as f:
                json.dump(config, f, indent=4)

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


def id_generation(type: str) -> str:
    """Generate a new ID for the given type.

    Args:
        type: One of "p" (problem), "s" (statement), "e" (experience)

    Returns:
        The new ID string (e.g., "p-003", "s-a001")
    """
    if type not in TYPE_MAP:
        raise ValueError(f"Invalid type '{type}'. Expected one of: {list(TYPE_MAP.keys())}")

    config = ensure_config()
    config_key = TYPE_MAP[type]

    current_id = config[config_key]
    new_id = increment_id(current_id)

    config[config_key] = new_id
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)

    return new_id
