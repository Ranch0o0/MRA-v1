# Upgrades on problem initialization

## Meta Info
- **Script** `src/prob_init.py` (already exists) and `src/prob_utils.py` (New)

## Instruction
1. Make id-creation a separate function
In `src/prob_utils.py`, build a function id_generation()
- It takes a param `type: str`, expecting three values "p", "s", "e" (problem, statement, experience)
- It load the file `contents/config.json` to read the current id.
- It performs the add-one operation, returnning the new id and update the config.json file.

**Special updates**
- Current indices go from 001 to 999. To allow more indices, please do the following:
    - If the number reaches 999, add-one operator add an English letter before the numbers. E.g. "p-999" -> "p-a001"
    - If the English letter already exists, switch to the next letter. E.g. "p-c999" -> "p-d001".
    - If reaching "z999", switch to "aa001".

- Update the config.json to expect value to be string instead of number.

2. In `src/prob_init.py` import the new id-creation function from `src/prob_utils.py`.

---

# Implementation Plan

## Clarifications
- **Config format:** Store full ID as string (e.g., `"p-002"`, `"s-a001"`)
- **Multi-letter continuation:** After `z999`, continue with `aa001` → `aa999` → `ab001` → ... → `az999` → `ba001` → ... → `zz999`
- **ensure_config:** Move to `prob_utils.py` to centralize all config handling

## ID Progression Examples
```
p-001 → p-002 → ... → p-999 → p-a001 → p-a002 → ... → p-a999 → p-b001 → ...
→ p-z999 → p-aa001 → p-aa999 → p-ab001 → ... → p-az999 → p-ba001 → ... → p-zz999
```

## Step-by-Step Implementation

### Step 1: Create `src/prob_utils.py` with Helper Functions

#### 1.1 Constants
```python
CONFIG_PATH = "contents/config.json"
TYPE_MAP = {
    "p": "count_problems",
    "s": "count_statements",
    "e": "count_experiences"
}
```

#### 1.2 `ensure_config()` function
Move from `prob_init.py`:
- Create `contents/` folder if not exists
- Create `config.json` if not exists with initial values as strings: `"p-000"`, `"s-000"`, `"e-000"`
- Load and return config dict

#### 1.3 `increment_id(current_id: str) -> str` helper function
Parse and increment the counter part of an ID:
1. Split ID by `-` to get prefix and counter (e.g., `"p-a001"` → `"p"`, `"a001"`)
2. Parse counter into letter part and number part:
   - `"001"` → letters=`""`, number=`1`
   - `"a001"` → letters=`"a"`, number=`1`
   - `"aa001"` → letters=`"aa"`, number=`1`
3. Increment logic:
   - If number < 999: increment number
   - If number == 999:
     - If no letters: set letters=`"a"`, number=`1`
     - If letters exist: increment letters (like base-26), set number=`1`
       - `"a"` → `"b"`, `"z"` → `"aa"`, `"az"` → `"ba"`, `"zz"` → `"aaa"`
4. Return formatted ID: `f"{prefix}-{letters}{number:03d}"`

#### 1.4 `id_generation(type: str) -> str` main function
1. Validate `type` is one of `"p"`, `"s"`, `"e"`
2. Call `ensure_config()` to load config
3. Get current ID from config using `TYPE_MAP[type]`
4. Call `increment_id(current_id)` to get new ID
5. Update config with new ID
6. Save config to file
7. Return new ID

### Step 2: Update `src/prob_init.py`

#### 2.1 Remove moved code
- Remove `CONFIG_PATH` constant
- Remove `ensure_config()` function
- Remove `generate_problem_id()` function

#### 2.2 Add imports
```python
from prob_utils import id_generation
```

#### 2.3 Update `create_problem()` function
Replace:
```python
problem_id = generate_problem_id()
```
With:
```python
problem_id = id_generation("p")
```

#### 2.4 Keep `PROBLEM_FOLDER` constant
Still needed for saving problem files.

### Step 3: Update `contents/config.json` Format

Migrate from integer format:
```json
{
    "count_problems": 2,
    "count_statements": 0,
    "count_experiences": 0
}
```

To string format:
```json
{
    "count_problems": "p-002",
    "count_statements": "s-000",
    "count_experiences": "e-000"
}
```

**Note:** The `ensure_config()` function should handle migration: if it detects integer values, convert them to string format.

## File Structure After Implementation
```
src/
├── prob_init.py      (updated - imports from prob_utils)
├── prob_utils.py     (new - id_generation, ensure_config, increment_id)
└── cus_types_main.py (unchanged)

contents/
├── config.json       (updated format - string values)
└── problem/
    └── p-001.json, p-002.json, ...
```

## Test Plan

### Test 1: Basic ID generation
```bash
venv-python -c "from src.prob_utils import id_generation; print(id_generation('p'))"
```
Expected: `p-003` (since current is `p-002`)

### Test 2: Problem creation with new system
```bash
venv-python src/prob_init.py --hypothesis "Test hypothesis" --objectives "Test objective"
```
Expected: Creates `p-003.json`

### Test 3: Increment edge cases (unit tests in code)
- `"p-999"` → `"p-a001"`
- `"p-a999"` → `"p-b001"`
- `"p-z999"` → `"p-aa001"`
- `"p-az999"` → `"p-ba001"`
- `"p-zz999"` → `"p-aaa001"`