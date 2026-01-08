---
name: prob-setup-subgoal
description: Creates a new subproblem when the current problem is too complex. Use when agent-solve determines decomposition is needed. Creates child problem and links it to parent's preliminaries.
---

# Create Subproblem

Creates a new subproblem when the current problem requires decomposition.

## Workflow

1. **Create the subproblem** using `src/prob.py`
2. **Link to parent** by updating the parent's `preliminaries` list

## Parameters Required

From the agent:
- `parent_problem_id`: The parent problem (e.g., `p-001`)
- `subproblem_objective`: What the subproblem should prove (list of strings)
- `subproblem_hypothesis`: Conditions inherited or specified for subproblem (list of strings)
- `rationale`: Why this decomposition helps

## Sample Commands

### Step 1: Create the subproblem

```bash
venv-python src/prob.py \
  --objectives "Prove that [a,b] is compact" \
  --hypothesis "(s-001) f is continuous on [a,b]" "[a,b] is a closed bounded interval in R" \
  --status unresolved \
  --priority "high"
```

Output: `Created problem: p-XXX` (or `Created problem: p-XXX [+N statements]` if new statements were created from hypothesis)

### Step 2: Link subproblem to parent's preliminaries

```bash
venv-python src/prob.py \
  --id p-001 \
  --preliminaries Append "p-XXX"
```

Output: `Updated p-001 [preliminaries] (log: log-XXX)`

## Output Format

Report to orchestrator:
```
DECOMPOSED: Problem [parent_id]
Created subproblem: [subproblem_id]
Subproblem objective: [what needs to be proved]
Rationale: [why this decomposition helps]
Status: Subproblem awaiting solution
```

## Notes

- Subproblem is created with `status = "unresolved"`
- Hypothesis items can reference existing statements with `(s-XXX)` prefix
- New statements are auto-created for hypothesis items without valid IDs
- The subproblem should be strictly simpler than the parent
- Multiple subproblems can be created for the same parent
