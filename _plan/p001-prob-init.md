# Problem initialization

## Meta Info
- **Script:** `src/prob_init.py`
- **Save folder:** `contents/problem`
- **Config file:** `contents/config.json`

## Instruction
1. Main block
- Set two terminal arguments:
    - hypothesis: list[str]
    - objectives: list[str]
- Use `argparse`:
```python
parser.add_argument('--hypothesis', nargs='+', type=str)
parser.add_argument('--objectives', nargs='+', type=str)
```
**Note**
    - This script is designed for agent to run. So only need to set terminal arguments.

2. Id creation:
- Check if the file `contents/config.json` exists. If not, create one:
```json
{
    "count_problems": 0,
    "count_statements": 0,
    "count_experiences": 0
}
```
**Note**
    - At the creation, set all counts to be zero.
    - This should be done before we create the id for new problem.

- Load the property `count_problems` and set id to be its value + 1.

3. Create a new problem
- Custom type `type_problem` already been created in `src/cus_type_main.py`.
- Use the `id`, `hypothesis`, and `objectives` properties to initialize a problem.
    - So all other properties are by default.
- Save the problem in `contents/problem` (check if folder exists first).

## Test
- Read the puzzle from `puzzle_test.md` and run the script with the puzzle.
    - You need to parse what is/are the hypothesis and what is/are the objective of the problem.

---

# Implementation Plan

## Clarifications
- **Filename correction:** The plan references `cus_type_main.py` but the actual file is `cus_types_main.py` (with an 's'). Will use the correct filename.
- **ID format:** Use format `problem-0001` (4 digits, zero-padded).
- **Save format:** JSON files.

## Step-by-Step Implementation

### Step 1: Import Dependencies
Import required modules in `src/prob_init.py`:
- `argparse` for command-line argument parsing
- `json` for reading/writing JSON files
- `os` for file/folder operations
- `dataclasses.asdict` for converting dataclass to dict (for JSON serialization)
- `type_problem` from `cus_types_main`

### Step 2: Implement Config File Handling
Create a function to handle the config file (`contents/config.json`):
1. Check if `contents/` folder exists; if not, create it
2. Check if `contents/config.json` exists
3. If not, create it with initial structure:
   ```json
   {
       "count_problems": 0,
       "count_statements": 0,
       "count_experiences": 0
   }
   ```
4. Load and return the config data

### Step 3: Implement ID Generation
Create a function to generate the next problem ID:
1. Read `count_problems` from config
2. Increment by 1
3. Format as `problem-XXXX` (4 digits, zero-padded)
4. Update `count_problems` in config file
5. Return the new ID

### Step 4: Implement Problem Creation
Create a function to initialize and save a problem:
1. Generate new ID using Step 3
2. Create `type_problem` instance with:
   - `id`: generated ID
   - `hypothesis`: from command-line args
   - `objectives`: from command-line args
   - Other fields use defaults from dataclass
3. Check if `contents/problem/` folder exists; if not, create it
4. Convert dataclass to dict using `asdict()`
5. Save as JSON file: `contents/problem/{id}.json`

### Step 5: Implement Main Block
Set up the main execution block:
1. Create `argparse.ArgumentParser`
2. Add arguments:
   - `--hypothesis`: `nargs='+'`, `type=str`
   - `--objectives`: `nargs='+'`, `type=str`
3. Parse arguments
4. Call problem creation function
5. Print confirmation message with the created problem ID

## File Structure After Implementation
```
contents/
├── config.json
└── problem/
    └── problem-0001.json
```

## Test Plan
Parse the puzzle from `puzzle_test.md`:
> "I have three apples, and my sister have two more apples than I. How many apples do both of us have in total?"

**Hypothesis:**
- "I have three apples"
- "My sister has two more apples than I"

**Objective:**
- "Find the total number of apples both of us have"

**Test command:**
```bash
venv-python src/prob_init.py --hypothesis "I have three apples" "My sister has two more apples than I" --objectives "Find the total number of apples both of us have"
```

**Expected output:**
- `contents/config.json` created/updated with `count_problems: 1`
- `contents/problem/problem-0001.json` created with the problem data
