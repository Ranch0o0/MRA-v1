# Problem initialization refinement

## Meta Info
- **Script** `src/prob_init.py`

## Instruction
1. Add a param `initial: bool` for the terminal arguments.
    - Default: false
    - Expect that generically there is no such argument (so by default false).
2. For the hypothesis input, check if each item (str) starts with the pattern `(...)` (after stripping spaces at the beginning). 
- If so, compare if what inside "()" is a valid statement id.
    - If it is a valid id, IGNORE whatever content after the bracket, and read the `conclusion` property of the statement to be append after the bracket.
- If no valid statement id is given, then create a new statement by importing relevant functions from `scr/state_init.py`.
    - The whole item (str) put as `conclusion` property, empty the hypothesis for the new statement.
    - Set the type of the new statement according to the new param `initial`:
        - If initial == true, then set type = assumed.
        - If initial == false, then set type = normal.
    - After creating the new statement, add its id in the form "({{statement_id}}) {{statement_content}}".
3. If initial == true, after creating all new stategments, also transverse the json files, and set the `status` to be "true": the hypothesis of the initial problem are considered as by default true statement.

## Test
- Test the new script `prob_init.py` on both of the puzzles (with initial == true). Note you need to parse what are the hypothesis by yourself.
- Check if the problem as well as statements are generated as expected (when generating the problem, adding new statement automatically).

---

# Implementation Plan

## Clarifications
- **Type for initial statements:** Use `"assumption"` (matches existing VALID_TYPES)
- **Status value:** Set to string `"true"` (default is `"pending"`)
- **ID validation:** Check if statement file exists in `contents/statement/{id}.json`
- **Text replacement:** Replace entire item with `"({id}) {conclusion}"`, ignoring text after bracket

## Overview
The enhancement adds smart hypothesis handling to `prob_init.py`:
1. Parse hypothesis items for statement ID references `(s-XXX)`
2. Auto-create statements for hypothesis items without IDs
3. Mark initial problem statements as `"true"` status

## Step-by-Step Implementation

### Step 1: Add Helper Functions to `prob_init.py`

#### 1.1 Import additional dependencies
```python
import re
from state_init import create_statement
```

#### 1.2 `parse_statement_id(text: str) -> str | None`
Extract statement ID from text starting with `(s-...)`:
1. Strip leading spaces
2. Check if starts with `(`
3. Use regex to extract ID pattern: `r'^\(([se]-[a-z]*\d+)\)'`
4. Return ID if found, else None

#### 1.3 `load_statement_conclusion(statement_id: str) -> str | None`
Load conclusion from statement file:
1. Build path: `contents/statement/{statement_id}.json`
2. Check if file exists
3. Load JSON and extract `conclusion` field (list)
4. Join list items with space and return
5. Return None if file doesn't exist or error

#### 1.4 `process_hypothesis_item(item: str, initial: bool) -> str`
Process single hypothesis item:
1. Call `parse_statement_id(item)` to check for ID
2. If ID found:
   - Call `load_statement_conclusion(id)`
   - If conclusion loaded: return `f"({id}) {conclusion}"`
   - Else: **ID format valid but file doesn't exist, strip invalid ID and create new statement**
3. If no valid ID (or invalid ID was stripped):
   - **Remove the invalid ID prefix if it exists** (e.g., `"(s-999) xxx"` → `"xxx"`)
   - Strip the cleaned text
   - Determine type: `"assumption"` if `initial==True`, else `"normal"`
   - Call `create_statement(type=type, conclusion=[cleaned_text], hypothesis=None)`
   - Get returned `statement_id`
   - Return `f"({statement_id}) {cleaned_text}"`

#### 1.5 `set_statement_status_true(statement_ids: list[str])`
Mark statements as true:
1. For each statement ID in list:
   - Build path: `contents/statement/{id}.json`
   - Load JSON
   - Set `status = "true"`
   - Save JSON back to file

### Step 2: Update `create_problem()` Function

Modify signature:
```python
def create_problem(
    hypothesis: list[str],
    objectives: list[str],
    initial: bool = False
) -> str:
```

Logic updates:
1. Process hypothesis items:
   ```python
   processed_hypothesis = []
   created_statement_ids = []

   for item in hypothesis:
       processed_item = process_hypothesis_item(item, initial)
       processed_hypothesis.append(processed_item)

       # Extract ID from processed item for status update
       id_match = re.match(r'^\(([se]-[a-z]*\d+)\)', processed_item)
       if id_match:
           created_statement_ids.append(id_match.group(1))
   ```

2. Create problem with processed hypothesis:
   ```python
   problem = type_problem(
       id=problem_id,
       hypothesis=processed_hypothesis,
       objectives=objectives
   )
   ```

3. If `initial==True`, update statement statuses:
   ```python
   if initial:
       set_statement_status_true(created_statement_ids)
   ```

### Step 3: Update Main Block

Add `--initial` argument:
```python
parser.add_argument('--initial', action='store_true', default=False)
```

Update function call:
```python
problem_id = create_problem(
    args.hypothesis,
    args.objectives,
    args.initial
)
```

## File Changes Summary

**Modified:**
- `src/prob_init.py`:
  - Add imports: `re`, `create_statement` from `state_init`
  - Add 4 helper functions
  - Update `create_problem()` signature and logic
  - Update main block with `--initial` argument

**Unchanged:**
- `src/state_init.py`
- `src/prob_utils.py`
- `src/cus_types_main.py`

## Test Plan

### Test 1: Basic hypothesis without IDs (initial=True)
Parse `puzzle_test.md`:
> "I have three apples, and my sister have two more apples than I."

**Hypothesis:**
- "I have three apples"
- "My sister has two more apples than I"

**Objectives:**
- "Find the total number of apples both of us have"

**Command:**
```bash
venv-python src/prob_init.py \
  --hypothesis "I have three apples" "My sister has two more apples than I" \
  --objectives "Find the total number of apples both of us have" \
  --initial
```

**Expected:**
1. Creates 2 new statements (`s-001`, `s-002`) with type `"assumption"`
2. Both statements have status `"true"`
3. Creates problem `p-001` with hypothesis:
   - `"(s-001) I have three apples"`
   - `"(s-002) My sister has two more apples than I"`

### Test 2: Hypothesis with existing statement ID reference
**Command:**
```bash
venv-python src/prob_init.py \
  --hypothesis "(s-001) anything here is ignored" "New hypothesis" \
  --objectives "Some objective"
```

**Expected:**
1. First hypothesis: loads `s-001` conclusion, formats as `"(s-001) I have three apples"`
2. Second hypothesis: creates `s-003` with type `"normal"`, formats as `"(s-003) New hypothesis"`
3. Only `s-003` has status `"pending"` (not initial, so no status update)
4. Creates `p-002`

### Test 3: Invalid statement ID reference
**Command:**
```bash
venv-python src/prob_init.py \
  --hypothesis "(s-999) nonexistent" \
  --objectives "Test" \
  --initial
```

**Expected:**
1. `s-999` doesn't exist, so **strips invalid ID** and creates new statement `s-004` with conclusion `"nonexistent"`
2. Statement type is `"assumption"` (initial=True)
3. Statement status is `"true"`
4. Problem hypothesis: `"(s-004) nonexistent"` (invalid ID removed)

### Test 4: Verify statement status updates
After Test 1, verify files:
- `contents/statement/s-001.json` has `"status": "true"`
- `contents/statement/s-002.json` has `"status": "true"`
- `contents/problem/p-001.json` has processed hypothesis with IDs