---
name: state-mark-false
description: Marks a statement as false when a counterexample is found. Use when agent-prove or agent-fix discovers the statement is unprovable due to being actually false. Records the counterexample and updates status.
---

# Mark Statement as False

Marks a statement as false when a counterexample is found.

## Workflow

1. **Update the statement** to set `status = "false"` and record the counterexample
2. **If called from fix agent**: Also record the response in `validation.responses`

## Parameters Required

From the agent:
- `statement_id`: The statement that is false (e.g., `s-001`)
- `counterexample`: Description of the counterexample
- `source`: "prove" or "fix" (which agent called this)
- `issue_number`: (optional, for fix agent) Which issue revealed this

## Sample Commands

### When called from agent-prove

```bash
venv-python src/state.py \
  --id s-001 \
  --status false \
  --progresses Append "COUNTEREXAMPLE: Let f(x)=x on [0,1]. f is continuous but the claim 'f attains value 2' is false since max(f)=1."
```

Output: `Updated s-001 [progresses,status] (log: log-XXX)`

### When called from agent-fix (with validation tracking)

```bash
venv-python src/state.py \
  --id s-001 \
  --status false \
  --progresses Append "COUNTEREXAMPLE: f(x)=x on [0,1] shows max is 1, not 2." \
  --validation.responses Append "[Response #1] Fixes Issue #1 | Type: false | Counterexample: f(x)=x on [0,1] has max=1, contradicting claim."
```

Output: `Updated s-001 [progresses,status,validation] (log: log-XXX)`

### Response format structure (for fix agent)

```
[Response #N] Fixes Issue #M | Type: false | Counterexample: <description>
```

## Output Format

### From agent-prove:
```
FALSE: Statement [statement_id] is unprovable - counterexample found.
Claim: [the claim]
Counterexample: [description]
Impact: Parent problem/statement needs revision
```

### From agent-fix:
```
FALSE: Statement [statement_id] - counterexample found
Issue #[N] addressed: [issue description]
Gap revealed: Sentence [M] is actually false
Counterexample: [description]
Validation history: [X] issues, [X] responses (final)
Impact: Parent problem/statement needs revision
```

## Notes

- A false statement cannot be used as a lemma
- The parent problem or statement will need revision
- Provide a complete counterexample showing:
  1. Setup that satisfies all premises
  2. Why the conclusion fails in this case
- The orchestrator will handle parent notification
