---
name: fix-create-substatement
description: Creates a sub-statement to fill a gap identified by agent-check. Use when agent-fix determines the gap requires a non-trivial intermediate result. Records the response in validation.responses and links to parent's preliminaries.
---

# Create Sub-statement to Fill Gap

Creates a sub-statement when a gap requires more than 3 steps to fill.

## Workflow

1. **Create the sub-statement** using `src/state.py`
2. **Link to parent** by updating the parent's `preliminaries` list
3. **Record the fix response** in `validation.responses`
4. **Update parent status** to `awaiting_substatement`

## Parameters Required

From the agent:
- `parent_statement_id`: The statement with the gap (e.g., `s-001`)
- `issue_number`: Which issue this addresses
- `sub_claim`: The claim for the sub-statement
- `sub_premises`: Premises for the sub-statement
- `gap_location`: Which sentence the sub-statement will support
- `purpose`: How this sub-statement fills the gap

## Sample Commands

### Step 1: Create the sub-statement

```bash
venv-python src/state.py \
  --type normal \
  --conclusion "[a,b] is compact" \
  --hypothesis Overwrite "[a,b] is a closed bounded interval in R"
```

Output: `Created statement: s-XXX`

### Step 2: Link to parent and record response

```bash
venv-python src/state.py \
  --id s-001 \
  --status awaiting_substatement \
  --preliminaries Append "s-XXX" \
  --validation.responses Append "[Response #1] Fixes Issue #1 | Type: substatement | SubID: s-XXX | Purpose: Establishes compactness of [a,b] to justify extreme value theorem application at sentence 3."
```

Output: `Updated s-001 [preliminaries,status,validation] (log: log-XXX)`

### Response format structure

```
[Response #N] Fixes Issue #M | Type: substatement | SubID: <sub_statement_id> | Purpose: <purpose>
```

## Output Format

Report to orchestrator:
```
SUB-STATEMENT CREATED: Statement [parent_id] -> Sub-statement [sub_id]
Issue #[N] addressed: [issue description]
Gap location: Sentence [M]
Sub-statement claim: [the claim]
Purpose: Once proved, fills gap by [explanation]
Validation history: [X] issues, [X] responses (now balanced)
Status: Sub-statement awaiting proof by agent-prove
```

## Preconditions

Before using this skill, verify:
- [ ] The gap requires a non-trivial intermediate result
- [ ] Filling the gap would take more than 3 atomic steps
- [ ] The sub-statement is simpler than proving the gap directly
- [ ] Once proved, the sub-statement clearly fills the gap

## Notes

- Sub-statement is created with `status = "pending"` and `type = "normal"`
- The sub-statement should be strictly simpler than the parent
- Parent status changes to `awaiting_substatement` (not `awaiting_substatements`)
- The orchestrator will schedule agent-prove for the sub-statement
