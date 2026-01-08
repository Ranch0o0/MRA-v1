---
name: prob-wrapup-statement
description: Creates a statement that resolves a problem. Use when agent-solve determines a single statement can bridge the gap between hypothesis and objective. Invokes src/state.py to create the statement and src/prob.py to link it.
---

# Create Wrap-up Statement for Problem

Creates a new statement that, once proved, resolves the problem objective.

## Workflow

1. **Create the statement** using `src/state.py`
2. **Link to problem** by updating the problem's `progresses` list using `src/prob.py`

## Parameters Required

From the agent:
- `problem_id`: The problem to resolve (e.g., `p-001`)
- `claim`: The precise statement to be proved (list of strings)
- `premises`: Conditions assumed true for this statement (list of strings)
- `purpose`: How this statement completes the problem resolution

## Sample Commands

### Step 1: Create the statement

```bash
venv-python src/state.py \
  --type normal \
  --conclusion "If f is continuous on [a,b] then f attains its maximum" \
  --hypothesis Overwrite "f is continuous on [a,b]" "[a,b] is a closed bounded interval"
```

Output: `Created statement: s-XXX`

### Step 2: Link statement to problem's progresses

```bash
venv-python src/prob.py \
  --id p-001 \
  --progresses Append "s-XXX"
```

Output: `Updated p-001 [progresses] (log: log-XXX)`

## Output Format

Report to orchestrator:
```
STATEMENT CREATED: Problem [problem_id] -> Statement [statement_id]
Claim: [the claim]
Purpose: [how this resolves the problem]
Status: Statement awaiting proof by agent-prove
```

## Notes

- Statement is created with `status = "pending"` and `type = "normal"`
- The claim should be precise enough for agent-prove to prove directly
- Premises should include all conditions needed from the problem's hypothesis
