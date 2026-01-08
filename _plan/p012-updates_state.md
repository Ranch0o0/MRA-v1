# Updates on statement dataclass
- Add validation properties

## Meta Info
- **Relevant Scripts** 
    - `src/cus_types_main.py` (already changed)
    - `src/state.py` (need change)
    - `src/current.py` (need change)
    - `src/utils.py` (check if any changes needed)

## Changes in dataclass (in `src/cus_types_main.py`):
- `type_validation`: new class recording validation process
- `type_statement`:
    - Add a new property `preliminaries`, to record sub-statements creating during the validation process.
    - Add a new property `validation`, to record the validation process.

## Instruction
1. `src/state.py` 
- Add three params to be received via terminal arguments (refer to `_plan/old/p009-refine-script-feedback.md`) for current setup.
    - prelimilaries: list[str]
        - mode: multiple
    - validation.issues: list[str]
        - mode: multiple
    - validation.responses: list[str]
        - mode: multiple

2. `src/current.py`
- Objective for this script is to print a report for the agent to know what are the "top-layer" problems and statements to be handled.

- Old behavior: 
    - For statements, filter `status == "pending"`
    - For problems, filter `status = "unresolved"` and `preliminaries == []`.

- New behavior:
    - First filter according to status:
        - For problems, keep filtering `status = "unresolved"`
        - For statements, filter `status == "pending" | "validating"` <- Involving statement during validation process as well.
    - Then filter according to preliminaries: 
        - For problems, if it has ANY preliminary problem which has `status != "resolved"`, then pass this problem (do not print in the final report)
        - For statements, if it has ANY preliminary statement which has `status != "true"`, then pass this statement (do not print in the final report)
    - Explanation: the logic is that if preliminary problems or statements still need care, do not need to be printed in the final report, but if all preliminaries have already been handled, the original object is on the top layer to be reported.

- For statements with `status == "validating"`, we now also check the property `validation`.
    - Compare the length between issues and responses: if len(issues) > len (responses), print with clear notice that there are unresolved validation issues.
    - If len(issues) == len (responses) (including the situation they are both zero), print with clear notice that a new checker is waited to be called to examine the last response.
    - Error handlement: if len(issues) < len (responses) print a clear warning that this is not supposed to happen. Ask agent to further inspect.

3. Please check if any other scripts (especially `src/utils.py`) needs any changes.

---

# Implementation Plan

## Pre-requisite Fix

### Fix missing default in `src/cus_types_main.py`
**Issue**: `type_statement.preliminaries` is declared without a default value, which will cause errors when creating statements without explicitly providing this field.

**Change**:
```python
# Line 33: Change from
preliminaries: list[str]

# To
preliminaries: list[str] = field(default_factory=list)
```

---

## Task 1: Update `src/state.py`

### 1.1 Add new arguments to argparse

Add three new multiple-value parameters following the existing pattern (mode + values):

```python
# After line 322 (existing --proof.ref argument)
parser.add_argument('--preliminaries', nargs='+', type=str,
                    help='Mode (Overwrite/Append) followed by preliminary statement IDs')
parser.add_argument('--validation.issues', nargs='+', type=str, dest='validation_issues',
                    help='Mode (Overwrite/Append) followed by validation issues')
parser.add_argument('--validation.responses', nargs='+', type=str, dest='validation_responses',
                    help='Mode (Overwrite/Append) followed by validation responses')
```

### 1.2 Update `handle_statement` function signature

Add new parameters to the function signature (around line 35-45):

```python
def handle_statement(
    id: Optional[str] = None,
    type: Optional[str] = None,
    conclusion: Optional[list[str]] = None,
    status: Optional[str] = None,
    reliability: Optional[float] = None,
    hypothesis: Optional[tuple[str, list[str]]] = None,
    proof_cot: Optional[tuple[str, list[str]]] = None,
    proof_full: Optional[str] = None,
    proof_ref: Optional[tuple[str, list[str]]] = None,
    preliminaries: Optional[tuple[str, list[str]]] = None,       # NEW
    validation_issues: Optional[tuple[str, list[str]]] = None,   # NEW
    validation_responses: Optional[tuple[str, list[str]]] = None, # NEW
    root_change: bool = True
) -> str | tuple[str, list[type_object_change]]:
```

### 1.3 Update `_create_statement` function

Add handling for new parameters in create mode (around lines 94-153):

```python
# After handling proof fields (around line 140)
# Handle preliminaries if provided
if preliminaries is not None:
    _, values = preliminaries
    statement.preliminaries = list(values)

# Handle validation fields if provided
if validation_issues is not None:
    _, values = validation_issues
    statement.validation.issues = list(values)
if validation_responses is not None:
    _, values = validation_responses
    statement.validation.responses = list(values)
```

### 1.4 Update `_update_statement` function

Add handling for new parameters in update mode (around lines 184-252):

```python
# After line 225 (after proof_ref handling)
if preliminaries is not None:
    updates["preliminaries"] = preliminaries
if validation_issues is not None:
    updates["validation.issues"] = validation_issues
if validation_responses is not None:
    updates["validation.responses"] = validation_responses
```

### 1.5 Update `build_args_from_parsed` function

Add parsing for new arguments (around lines 255-294):

```python
# After line 292 (after proof_ref handling)
if args.preliminaries:
    mode = args.preliminaries[0]
    values = args.preliminaries[1:]
    kwargs["preliminaries"] = (mode, values)
if args.validation_issues:
    mode = args.validation_issues[0]
    values = args.validation_issues[1:]
    kwargs["validation_issues"] = (mode, values)
if args.validation_responses:
    mode = args.validation_responses[0]
    values = args.validation_responses[1:]
    kwargs["validation_responses"] = (mode, values)
```

### 1.6 Pass new parameters through function calls

Update the calls in `handle_statement` to `_create_statement` and `_update_statement` to include the new parameters.

---

## Task 2: Update `src/current.py`

### 2.1 Update `get_pending_statements` function

Rename and modify to filter both "pending" and "validating" statements:

```python
def get_actionable_statements(statements: list[dict]) -> list[dict]:
    """Filter statements that need attention (pending or validating).

    Actionable statements are:
    - status = "pending" OR "validating"
    - All preliminary statements (if any) have status = "true"
    """
    actionable = []

    # Create a lookup dict for quick status checks
    statement_lookup = {s["id"]: s for s in statements}

    for s in statements:
        status = s.get("status")

        # First filter: status must be "pending" or "validating"
        if status not in ("pending", "validating"):
            continue

        # Second filter: check preliminaries
        preliminaries = s.get("preliminaries", [])
        all_prelim_resolved = True

        for prelim_id in preliminaries:
            prelim = statement_lookup.get(prelim_id)
            if prelim and prelim.get("status") != "true":
                all_prelim_resolved = False
                break

        if all_prelim_resolved:
            actionable.append(s)

    return actionable
```

### 2.2 Update `get_actionable_problems` function

**IMPORTANT**: Problem preliminaries can be either problems OR statements. We need to check both and use appropriate status checks.

Modify to check preliminary statuses (both problems and statements):

```python
def get_actionable_problems(problems: list[dict], statements: list[dict]) -> list[dict]:
    """Filter problems that are actionable.

    Actionable problems are:
    - status = "unresolved"
    - All preliminaries have their required status:
      - Preliminary problems: status = "resolved"
      - Preliminary statements: status = "true"
    """
    # Create lookup dicts for quick status checks
    problem_lookup = {p["id"]: p for p in problems}
    statement_lookup = {s["id"]: s for s in statements}

    actionable = []
    for p in problems:
        # First filter: status must be "unresolved"
        if p.get("status") != "unresolved":
            continue

        # Second filter: check preliminaries (can be problems or statements)
        preliminaries = p.get("preliminaries", [])
        all_prelim_resolved = True

        for prelim_id in preliminaries:
            # Check if it's a problem
            if prelim_id.startswith("p-"):
                prelim = problem_lookup.get(prelim_id)
                if prelim and prelim.get("status") != "resolved":
                    all_prelim_resolved = False
                    break
            # Check if it's a statement
            elif prelim_id.startswith("s-"):
                prelim = statement_lookup.get(prelim_id)
                if prelim and prelim.get("status") != "true":
                    all_prelim_resolved = False
                    break

        if all_prelim_resolved:
            actionable.append(p)

    return actionable
```

### 2.3 Update `display_statements` function

Modify to handle "validating" status and show validation state:

```python
def display_statements(statements: list[dict]) -> None:
    """Display statement info: id, conclusion, and validation status if applicable."""
    print("=== Actionable Statements ===")

    if not statements:
        print("\n(none)")
        return

    for s in statements:
        print(f"\n[{s['id']}]")

        # Status indicator
        status = s.get("status", "pending")

        # Conclusion
        print("  Conclusion:")
        conclusions = s.get("conclusion", [])
        if conclusions:
            for conc in conclusions:
                print(f"    - {conc}")
        else:
            print("    (none)")

        # For validating statements, show validation status
        if status == "validating":
            validation = s.get("validation", {})
            issues = validation.get("issues", [])
            responses = validation.get("responses", [])

            len_issues = len(issues)
            len_responses = len(responses)

            print("  Validation Status:")
            if len_issues > len_responses:
                # Unresolved issues exist
                print(f"    [!] UNRESOLVED ISSUES: {len_issues - len_responses} issue(s) awaiting response")
                print(f"    (issues: {len_issues}, responses: {len_responses})")
            elif len_issues == len_responses:
                # All issues addressed, awaiting checker
                print(f"    [*] AWAITING CHECKER: All {len_issues} issue(s) have responses")
                print(f"    Call checker to examine the latest response")
            else:
                # Error: more responses than issues
                print(f"    [WARNING] INVALID STATE: More responses ({len_responses}) than issues ({len_issues})")
                print(f"    Please inspect this statement manually")
```

### 2.4 Update `show_current_status` function

Update to use the renamed function and pass both problems and statements to `get_actionable_problems`:

```python
def show_current_status() -> None:
    """Main function to display current status."""
    # Load all objects
    problems = load_all_problems()
    statements = load_all_statements()

    # Filter
    actionable_problems = get_actionable_problems(problems, statements)  # Pass both!
    actionable_statements = get_actionable_statements(statements)

    # Check for edge case: no actionable items
    if not actionable_problems and not actionable_statements:
        # ... rest unchanged
```

### 2.5 Update header in display

Change "Pending Statements" to "Actionable Statements" in the display function (already done in 2.3).

---

## Task 3: Check `src/utils.py`

After review, **no changes are needed** for `src/utils.py`. The existing `apply_updates` function already handles:
- Nested field paths like `validation.issues` and `validation.responses`
- Mode tuples for list fields (overwrite/append)

The existing infrastructure is sufficient for the new fields.

---

## Summary of Changes

| File | Change Type | Description |
|------|-------------|-------------|
| `src/cus_types_main.py` | Fix | Add `= field(default_factory=list)` to `preliminaries` |
| `src/state.py` | Add args | 3 new CLI args: `--preliminaries`, `--validation.issues`, `--validation.responses` |
| `src/state.py` | Update functions | Handle new params in `handle_statement`, `_create_statement`, `_update_statement`, `build_args_from_parsed` |
| `src/current.py` | Rename function | `get_pending_statements` → `get_actionable_statements` |
| `src/current.py` | Update `get_actionable_problems` | Accept both problems and statements; check both problem and statement preliminaries with appropriate status checks |
| `src/current.py` | Update filter logic | Check preliminary statuses: problems→"resolved", statements→"true" |
| `src/current.py` | Update display | Show validation status for "validating" statements |
| `src/utils.py` | No change | Existing infrastructure already supports new fields |

---

## Testing Checklist

1. **Create statement with preliminaries**:
   ```bash
   venv-python src/state.py --type proposition --conclusion "Test" --preliminaries Overwrite s-001 s-002
   ```

2. **Update statement with validation issues**:
   ```bash
   venv-python src/state.py --id s-001 --validation.issues Append "Issue 1" --status validating
   ```

3. **Update statement with validation responses**:
   ```bash
   venv-python src/state.py --id s-001 --validation.responses Append "Response 1"
   ```

4. **Check current status displays correctly**:
   ```bash
   venv-python src/current.py
   ```
   - Verify pending statements with unresolved preliminaries are hidden
   - Verify validating statements show correct validation status