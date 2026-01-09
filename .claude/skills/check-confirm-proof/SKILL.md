---
name: check-confirm-proof
description: Confirms that a proof/disproof is valid and marks the statement accordingly. Use when agent-check has verified all sentences with no gaps found. Updates statement status to true (for proofs) or false (for disproofs).
---

# Confirm Valid Proof or Disproof

Marks a statement as verified after agent-check confirms all argument steps are valid.
- For PROOF: Sets `status = "true"`
- For DISPROOF: Sets `status = "false"`

## Workflow

1. **Determine direction** from the first sentence of the proof:
   - "We prove this statement as follows" → PROOF (status = true)
   - "This statement is wrong. We disprove as follows" → DISPROOF (status = false)

2. **Update the statement** to set appropriate status and record verification summary
3. **Record progress** with appropriate prefix (max 2 sentences)

## Parameters Required

From the agent:
- `statement_id`: The statement that was verified (e.g., `s-001`)
- `direction`: "proof" or "disproof" (determines status)
- `verification_summary`: Brief summary of verification (optional, for reference)

## Sample Commands

### Confirm proof is valid (statement is true)

```bash
venv-python src/state.py \
  --id s-001 \
  --status true \
  --reliability 1.0 \
  --progresses Append "VERIFIED: Proof establishes statement in 5 steps"
```

Output: `Updated s-001 [progresses,reliability,status] (log: log-XXX)`

### Confirm disproof is valid (statement is false)

```bash
venv-python src/state.py \
  --id s-001 \
  --status false \
  --reliability 1.0 \
  --progresses Append "DISPROOF VERIFIED: Counterexample found, statement is false"
```

Output: `Updated s-001 [progresses,reliability,status] (log: log-XXX)`

## Output Format

### For Proof
Report to orchestrator:
```
VERIFIED: Statement [statement_id] proof is valid.
The proof correctly establishes [claim] in [N] steps.
Status updated to: true
```

### For Disproof
Report to orchestrator:
```
DISPROOF VERIFIED: Statement [statement_id] is false.
The disproof successfully refutes [claim] in [N] steps.
Status updated to: false
Counterexample/Contradiction: [brief description]
```

## Notes

- For PROOF: Setting `status = "true"` means the statement can now be cited as a lemma
- For DISPROOF: Setting `status = "false"` records that the statement is provably false
- Set `reliability = 1.0` to indicate full confidence
- The orchestrator may now check if this enables problem resolution or requires revision
- Only call this after ALL sentences have been verified as valid
