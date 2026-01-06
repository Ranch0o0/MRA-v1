# Refine the utils system

## Meta Info
- **Script** `src/utils.py` (renamed from `src/prob_utils.py`)

## Instruction
- Wrap current functions in an instance.
- Make the record of ids instance variable of list[str] type.
- Create push and update functions that can be called by other part of the code:
    - This serves as the solo source of truth for the ids.
    - The instance variable is pushed to other places, and modified when creating new problems, statements, or experiences.
    - When updated, the new id counts are also saved to original config.json. (So only one file read at the initialization of the instance)

## Clarifications
- **ID list content**: Store current count IDs only (e.g., ['p-002', 's-013', 'e-000'])
- **Instance pattern**: Singleton pattern for single source of truth
- **Function consolidation**: Combine push and update into a unified `generate_id()` method that generates new IDs and persists to config.json

---

## Implementation Plan

### 1. Design the IDManager Class Structure

**File**: [src/utils.py](src/utils.py) (renamed from [src/prob_utils.py](src/prob_utils.py))

Create a singleton `IDManager` class with the following structure:

```python
class IDManager:
    _instance = None  # Singleton instance
    _initialized = False  # Prevent re-initialization

    def __new__(cls):
        # Implement singleton pattern

    def __init__(self):
        # Initialize only once
        # Read config.json and populate self._current_ids

    @property
    def current_ids(self) -> list[str]:
        # Return copy of current IDs for read-only access

    def generate_id(self, type: str) -> str:
        # Generate new ID, update instance variable, persist to config.json
        # This replaces the old id_generation() function
```

**Key design decisions**:
- Singleton ensures single source of truth across the application
- `_current_ids`: private instance variable storing `[problems_id, statements_id, experiences_id]`
- `current_ids` property: provides read-only access via copy
- `generate_id()`: unified method combining ID generation and persistence

### 2. Implement Core Class Components

#### 2.1 Singleton Pattern Implementation
- Use `__new__` to ensure only one instance exists
- Use `_initialized` flag to prevent re-initialization in `__init__`
- Thread-safe implementation not required (single-threaded CLI tool)

#### 2.2 Initialization Logic
- In `__init__`, call `ensure_config()` to read config.json once
- Parse config into `_current_ids` list in order: `[count_problems, count_statements, count_experiences]`
- Store config path as instance variable for updates

#### 2.3 Property for Read-Only Access
- Implement `current_ids` property that returns a copy of `_current_ids`
- This prevents external code from modifying the internal list directly

#### 2.4 ID Generation Method
- Implement `generate_id(type: str) -> str` method:
  1. Validate type parameter ('p', 's', 'e')
  2. Get current ID from `_current_ids` based on type
  3. Use existing `increment_id()` helper to generate new ID
  4. Update corresponding entry in `_current_ids` list
  5. Persist updated IDs back to config.json immediately
  6. Return the new ID

### 3. Refactor Helper Functions

**Keep as module-level functions** (no changes needed):
- `ensure_config()`: Used during initialization
- `increment_letters()`: Pure utility function
- `increment_id()`: Pure utility function
- `TYPE_MAP`: Module-level constant

**Rationale**: These are stateless utilities that don't need to be instance methods.

### 4. Rename File and Update All Imports

#### 4.1 Rename the file
- Rename `src/prob_utils.py` to `src/utils.py`

#### 4.2 Update [src/state_init.py](src/state_init.py:7)
Replace:
```python
from prob_utils import id_generation
```

With:
```python
from utils import IDManager
```

And update the usage at [src/state_init.py](src/state_init.py:32):
```python
# In create_statement():
id_manager = IDManager()
statement_id = id_manager.generate_id("s")
```

#### 4.3 Update [src/prob_init.py](src/prob_init.py:8)
Replace:
```python
from prob_utils import id_generation
```

With:
```python
from utils import IDManager
```

And update the usage at [src/prob_init.py](src/prob_init.py:148):
```python
# In create_problem():
id_manager = IDManager()
problem_id = id_manager.generate_id("p")
```

### 5. Backward Compatibility (Optional)

Add a module-level convenience function for backward compatibility:
```python
def id_generation(type: str) -> str:
    """Legacy function for backward compatibility."""
    return IDManager().generate_id(type)
```

This allows existing code to work without modifications if needed.

### 6. Testing Strategy

**Manual tests to perform**:
1. Test singleton behavior: verify multiple `IDManager()` calls return same instance
2. Test ID generation: create problem and statement, verify IDs increment correctly
3. Test persistence: check config.json is updated after each generation
4. Test initialization: verify config.json is read only once (add debug logging if needed)
5. Test the `current_ids` property returns correct values
6. Test invalid type parameter raises appropriate error

**Test scenarios**:
- Create multiple statements in sequence
- Create alternating problems and statements
- Verify config.json reflects latest counts after each operation

### 7. File Structure Summary

**Renamed file**:
- `src/prob_utils.py` → `src/utils.py`

**Modified files**:
- [src/utils.py](src/utils.py): Add IDManager class (renamed from prob_utils.py)
- [src/state_init.py](src/state_init.py:7,32): Update import from `prob_utils` to `utils` and usage
- [src/prob_init.py](src/prob_init.py:8,148): Update import from `prob_utils` to `utils` and usage

**No new files needed**: All changes are in-place refactoring with one file rename

---

## Implementation Order

1. Implement `IDManager` class in [src/prob_utils.py](src/prob_utils.py)
   - Singleton pattern
   - Initialization with config loading
   - `current_ids` property
   - `generate_id()` method

2. Rename `src/prob_utils.py` to `src/utils.py`

3. Update [src/state_init.py](src/state_init.py) imports and usage
   - Change `from prob_utils import id_generation` to `from utils import IDManager`
   - Update function call to use `IDManager().generate_id("s")`

4. Update [src/prob_init.py](src/prob_init.py) imports and usage
   - Change `from prob_utils import id_generation` to `from utils import IDManager`
   - Update function call to use `IDManager().generate_id("p")`

5. Manual testing with sample problem/statement creation

6. Optional: Add backward compatibility wrapper if needed

---

## Expected Benefits

- **Single source of truth**: Singleton ensures consistent ID state across application
- **Performance**: Config.json read only once at initialization
- **Maintainability**: Encapsulated state management in clear class structure
- **Type safety**: Instance variable provides clear interface for ID access
- **Atomic updates**: Each `generate_id()` call persists immediately to prevent data loss

---

## Post-Implementation Simplification

After initial implementation, the following simplification was made:

### Simplified config.json Structure

**Changed from**:
```json
{
    "count_problems": "p-003",
    "count_statements": "s-017",
    "count_experiences": "e-000"
}
```

**To**:
```json
{
    "p": "p-003",
    "s": "s-017",
    "e": "e-000"
}
```

**Rationale**: Using "p", "s", "e" directly as keys eliminates redundant mapping logic.

### Code Simplifications in [src/utils.py](src/utils.py)

1. **Removed redundant mappings**:
   - Removed `TYPE_MAP` dict (was mapping "p" → "count_problems", etc.)
   - Removed `TYPE_TO_INDEX` dict (was mapping "p" → 0, etc.)
   - Replaced with simple `VALID_TYPES = ["p", "s", "e"]`

2. **Changed internal storage**:
   - Changed `_current_ids` from `list[str]` to `dict[str, str]`
   - Direct access via `self._current_ids[type]` instead of index lookup
   - Property `current_ids` now returns `dict[str, str]` instead of `list[str]`

3. **Simplified `generate_id()` method**:
   - Direct dictionary access: `self._current_ids[type]`
   - Direct persistence: `json.dump(self._current_ids, f, indent=4)`
   - No need to reconstruct config dict

4. **Removed migration logic**:
   - Removed integer-to-string migration code from `ensure_config()`
   - Cleaner initialization

**Result**: ~30 lines of code removed, clearer and more maintainable implementation.