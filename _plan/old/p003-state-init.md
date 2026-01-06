# Create statements

## Meta Info
- **Script:** `src/state_init.py`
- **Save folder:** `contents/statement`
- **Config file:** `contents/config.json`

## Instruction
1. Main block
- Set two terminal arguments:
    - type: str
    - hypothesis: list[str]
    - content: list[str]
- Use `argparse`:
```python
parser.add_argument('--type', nargs='1', type=str)
parser.add_argument('--hypothesis', nargs='+', type=str)
parser.add_argument('--content', nargs='+', type=str)
```
**Note**
    - This script is designed for agent to run. So only need to set terminal arguments.
    - Please handle the situation that there might be no hypothesis.
    - Please make the function to add a new statement importable: in the future, creating a new problem will automatically add all of its hypothesis as statements.

2. Id creation:
- Import the function from `prob_utils.py`

3. Create a new statement
- Custom type `type_statement` already been created in `src/cus_types_main.py`.
- Use the `id`, `type`, `hypothesis` (possibly empty, in which case use the default value in the custom class), and `content` properties to initialize a problem.
    - So all other properties are by default.
- Save the statement in `contents/statement` (check if folder exists first).

## Test
- Read the puzzle from `puzzle_test.md` and run the script with the puzzle.
    - You need to parse what is/are the hypothesis = statement(s) of the problem: statement only, and for statement object, on hypothesis part.

---

# Implementation Plan

## Clarifications
- **Argument naming:** Use `--conclusion` to match the dataclass field (not `--content`)
- **Type argument:** Use simple `type=str` without `nargs` for single value
- **Type values:** Validate against `["assumption", "proposition", "normal"]`

## Step-by-Step Implementation

### Step 1: Create `src/state_init.py`

#### 1.1 Imports
```python
import argparse
import json
import os
from dataclasses import asdict

from cus_types_main import type_statement
from prob_utils import id_generation
```

#### 1.2 Constants
```python
STATEMENT_FOLDER = "contents/statement"
VALID_TYPES = ["assumption", "proposition", "normal"]
```

#### 1.3 `create_statement()` function (importable)
```python
def create_statement(
    type: str,
    conclusion: list[str],
    hypothesis: list[str] | None = None
) -> str:
```

Function logic:
1. Validate `type` is in `VALID_TYPES`
2. Generate ID using `id_generation("s")`
3. Create `type_statement` instance:
   - `id`: generated ID
   - `type`: from argument
   - `conclusion`: from argument
   - `hypothesis`: from argument or empty list (default)
4. Create `contents/statement/` folder if not exists
5. Save as JSON: `contents/statement/{id}.json`
6. Return the new ID

#### 1.4 Main block with argparse
```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize a new statement")
    parser.add_argument('--type', type=str, required=True, choices=VALID_TYPES)
    parser.add_argument('--conclusion', nargs='+', type=str, required=True)
    parser.add_argument('--hypothesis', nargs='+', type=str, default=None)

    args = parser.parse_args()

    statement_id = create_statement(
        type=args.type,
        conclusion=args.conclusion,
        hypothesis=args.hypothesis
    )
    print(f"Created statement: {statement_id}")
```

**Notes:**
- `--hypothesis` is optional (default=None), handled gracefully
- `--type` uses `choices` for validation
- Function `create_statement()` is importable for use in `prob_init.py`

## File Structure After Implementation
```
src/
├── state_init.py     (new - statement initialization)
├── prob_init.py      (unchanged for now)
├── prob_utils.py     (unchanged)
└── cus_types_main.py (unchanged)

contents/
├── config.json
├── problem/
│   └── p-001.json, ...
└── statement/
    └── s-001.json, ...
```

## Test Plan

### Test 1: Create statement with hypothesis
Parse from `puzzle_test.md`:
> "I have three apples, and my sister have two more apples than I."

These are assumptions (facts given), so type = "assumption".

**Test command:**
```bash
venv-python src/state_init.py --type assumption --conclusion "I have three apples"
```
Expected: Creates `s-001.json`

```bash
venv-python src/state_init.py --type assumption --conclusion "My sister has two more apples than I"
```
Expected: Creates `s-002.json`

### Test 2: Create statement without hypothesis
```bash
venv-python src/state_init.py --type proposition --conclusion "The total is 8 apples" --hypothesis "I have three apples" "My sister has five apples"
```
Expected: Creates `s-003.json` with hypothesis field populated

### Test 3: Invalid type validation
```bash
venv-python src/state_init.py --type invalid --conclusion "Test"
```
Expected: Error message about invalid choice

### Test 4: Verify config update
After tests, `contents/config.json` should show:
```json
{
    "count_problems": "p-003",
    "count_statements": "s-003",
    "count_experiences": "e-000"
}
```