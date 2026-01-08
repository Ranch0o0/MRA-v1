---
name: check-reject-proof
description: Records a gap found during proof verification. Use when agent-check identifies an invalid sentence in a proof. Appends issue to validate.issues and sets status to validating.
---

# Record Proof Gap

Records a gap or error found during proof verification by agent-check.

## Workflow

1. **Append the issue** to the statement's `validation.issues` list
2. **Keep status** as `validating` (status does not change)

## Parameters Required

From the agent:
- `statement_id`: The statement with the gap (e.g., `s-001`)
- `sentence_number`: Which sentence has the gap (1-indexed)
- `sentence_text`: The exact text of the problematic sentence
- `error_type`: One of: `gap`, `unjustified_leap`, `hidden_assumption`, `circular`, `scope_error`, `wrong_target`
- `explanation`: Detailed description of what's wrong
- `suggested_fix`: What would be needed to fix this

## Sample Commands

### Record a gap in the proof

The issue should be formatted as a structured string:

```bash
venv-python src/state.py \
  --id s-001 \
  --status validating \
  --validation.issues Append "[Issue #1] Sentence 3: 'By continuity, f attains max.' | Type: unjustified_leap | Explanation: Continuity alone doesn't imply max attainment; needs compactness. | Fix: Prove [a,b] is compact first."
```

Output: `Updated s-001 [status,validation] (log: log-XXX)`

### Issue format structure

```
[Issue #N] Sentence M: '<sentence_text>' | Type: <error_type> | Explanation: <explanation> | Fix: <suggested_fix>
```

## Output Format

Report to orchestrator:
```
REJECTED: Statement [statement_id] proof has a gap at sentence [N].
Error type: [type]
Issue: [brief explanation]
Suggested fix: [what's needed]
Validation history: [X] previous issues, [Y] responses
This is issue #[Z] for this statement
```

## Error Types

- `gap`: Conclusion doesn't follow from premises
- `unjustified_leap`: Multiple steps compressed into one
- `hidden_assumption`: Using facts not in premises
- `circular`: Proof assumes what it's trying to prove
- `scope_error`: Variables used outside quantifier scope
- `wrong_target`: Final conclusion doesn't match claim

## Notes

- Always identify the FIRST error, not all errors
- Issue numbers auto-increment based on existing issues
- The orchestrator will decide whether to invoke agent-fix
- Provide constructive feedback on what would fix the gap
