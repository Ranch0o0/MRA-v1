---
name: state-complete-proof
description: Submits a completed proof for verification. Use when agent-prove has written a full proof and is ready for agent-check to verify it. Updates the statement with proof text and sets status to awaiting_verification.
---

# Submit Completed Proof

Submits a proof for a statement, marking it ready for verification by agent-check.

## Workflow

1. **Update the statement** with proof text and set status to `awaiting_verification`

## Parameters Required

From the agent:
- `statement_id`: The statement being proved (e.g., `s-001`)
- `proof_text`: The complete proof (structured with steps)
- `strategy`: Proof strategy used (direct/contradiction/case_analysis/backward)
- `proof_cot`: Chain-of-thought reasoning steps (optional)
- `proof_ref`: References to other statements used (optional)

## Sample Commands

### Basic proof submission

```bash
venv-python src/state.py \
  --id s-001 \
  --status awaiting_verification \
  --proof.full "Let f be continuous on [a,b]. Since [a,b] is compact and f is continuous, f attains its maximum by the extreme value theorem. QED."
```

Output: `Updated s-001 [proof,status] (log: log-XXX)`

### With chain-of-thought and references

```bash
venv-python src/state.py \
  --id s-001 \
  --status awaiting_verification \
  --proof.full "Step 1: By premise, f is continuous. Step 2: By s-002, [a,b] is compact. Step 3: Continuous functions on compact sets attain their extrema. QED." \
  --proof.cot Overwrite "Identify premises" "Apply compactness lemma" "Conclude from extreme value theorem" \
  --proof.ref Overwrite "s-002"
```

Output: `Updated s-001 [proof,status] (log: log-XXX)`

## Output Format

Report to orchestrator:
```
PROOF SUBMITTED: Statement [statement_id]
Claim: [the claim]
Proof length: [N] steps
Strategy: [direct / contradiction / case_analysis / etc.]
Status: Awaiting verification by agent-check
```

## Notes

- The `validation` field is initialized automatically if not present
- Proof should be structured with clear steps for agent-check to verify
- Each step should cite its justification (premise, previous step, or lemma)
- Only cite statements with `status == "true"` as lemmas
