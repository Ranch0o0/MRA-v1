---
name: fix-patch-proof
description: Applies a direct fix to proof text. Use when agent-fix determines a gap can be fixed with minor additions (3 or fewer steps). Updates proof and records the response in validation.responses.
---

# Patch Proof Text

Applies a direct fix to the proof text when the gap is a minor omission.

## Workflow

1. **Update the proof** with corrected text
2. **Record the fix** in `validation.responses`
3. **Keep status** as `validating` (status does not change)

## Parameters Required

From the agent:
- `statement_id`: The statement to fix (e.g., `s-001`)
- `issue_number`: Which issue this fixes (from validation.issues)
- `updated_proof`: The complete updated proof text
- `change_description`: Brief description of what was changed

## Sample Commands

### Apply the patch and record response

```bash
venv-python src/state.py \
  --id s-001 \
  --status validating \
  --proof.full "Step 1: f is continuous on [a,b] (given). Step 2: [a,b] is closed and bounded, hence compact by Heine-Borel. Step 3: By extreme value theorem, continuous functions on compact sets attain their maximum. QED." \
  --validation.responses Append "[Response #1] Fixes Issue #1 | Type: patch | Change: Added Step 2 to establish compactness via Heine-Borel before applying EVT."
```

Output: `Updated s-001 [proof,status,validation] (log: log-XXX)`

### Response format structure

```
[Response #N] Fixes Issue #M | Type: patch | Change: <change_description>
```

## Output Format

Report to orchestrator:
```
FIXED: Statement [statement_id] - direct patch applied
Issue #[N] addressed: [issue description]
Gap location: Sentence [M]
Fix: Expanded into [K] steps
Change: [brief description of what was added]
Validation history: [X] issues, [X] responses (now balanced)
Status: Proof updated, awaiting re-verification by agent-check
```

## Preconditions

Before using this skill, verify:
- [ ] The gap is a minor omission (not missing logic)
- [ ] The fix requires at most 3 additional atomic steps
- [ ] No new concepts or lemmas are needed
- [ ] The fix is straightforward to verify

## Notes

- The fix must reconnect properly to the rest of the proof
- Keep the fix minimal (no unnecessary additions)
- Response numbers auto-increment based on existing responses
- The orchestrator will schedule agent-check to re-verify
