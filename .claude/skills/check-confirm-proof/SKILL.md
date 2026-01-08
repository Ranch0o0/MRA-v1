---
name: check-confirm-proof
description: Confirms that a proof is valid and marks the statement as true. Use when agent-check has verified all sentences in a proof with no gaps found. Updates statement status to true.
---

# Confirm Valid Proof

Marks a statement as verified and true after agent-check confirms all proof steps are valid.

## Workflow

1. **Update the statement** to set `status = "true"` and record verification summary
2. **Record progress** with `VERIFIED:` prefix (max 2 sentences)

## Parameters Required

From the agent:
- `statement_id`: The statement that was verified (e.g., `s-001`)
- `verification_summary`: Brief summary of verification (optional, for reference)

## Sample Commands

### Confirm proof is valid

```bash
venv-python src/state.py \
  --id s-001 \
  --status true \
  --reliability 1.0
```

Output: `Updated s-001 [reliability,status] (log: log-XXX)`

### With verification notes in progresses

```bash
venv-python src/state.py \
  --id s-001 \
  --status true \
  --reliability 1.0 \
  --progresses Append "VERIFIED: 5 steps checked, all valid"
```

Output: `Updated s-001 [progresses,reliability,status] (log: log-XXX)`

## Output Format

Report to orchestrator:
```
VERIFIED: Statement [statement_id] proof is valid.
The proof correctly establishes [claim] in [N] steps.
```

## Notes

- Setting `status = "true"` means the statement can now be cited as a lemma
- Set `reliability = 1.0` to indicate full confidence
- The orchestrator may now check if this enables problem resolution
- Only call this after ALL sentences have been verified as valid
