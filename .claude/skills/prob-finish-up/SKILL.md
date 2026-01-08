---
name: prob-finish-up
description: Marks a problem as resolved after a key statement has been proved. Use when agent-solve confirms a statement with status=true enables problem resolution. Updates problem status to resolved.
---

# Mark Problem as Resolved

Marks a problem as resolved after a key statement has been proved.

## Workflow

1. **Verify** the key statement has `status == "true"`
2. **Update the problem** to set `status = "resolved"` and record the resolution

## Parameters Required

From the agent:
- `problem_id`: The problem to mark as resolved (e.g., `p-001`)
- `resolution`: Text explaining how the objective follows from the proved statement
- `key_statement_id`: ID of the statement (with status="true") that enables resolution

## Sample Commands

### Mark problem as resolved

```bash
venv-python src/prob.py \
  --id p-001 \
  --status resolved \
  --solution.full "The objective follows from s-001: since f is continuous on [a,b] (proved), f attains its maximum by the extreme value theorem." \
  --solution.ref Overwrite "s-001"
```

Output: `Updated p-001 [solution,status] (log: log-XXX)`

### With chain-of-thought summary

```bash
venv-python src/prob.py \
  --id p-001 \
  --status resolved \
  --solution.full "Objective achieved via s-001" \
  --solution.cot Overwrite "s-001 proves continuity implies max" "This directly resolves the objective" \
  --solution.ref Overwrite "s-001"
```

Output: `Updated p-001 [solution,status] (log: log-XXX)`

## Output Format

Report to orchestrator:
```
RESOLVED: Problem [problem_id]
Objective: [the objective]
Key statement used: [statement_id] (status == "true")
Resolution: [brief description of how objective follows]
```

## Preconditions

Before using this skill, verify:
- [ ] The key statement has `status == "true"`
- [ ] The resolution from statement to objective is purely mechanical (no new reasoning)
- [ ] All logical steps are tautological

## Notes

- Only mark resolved when the resolution requires NO new logical deduction
- The `solution.ref` should include all statements used in the resolution
- If any step requires non-trivial reasoning, create another statement instead
