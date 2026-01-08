---
name: state-propose-modification
description: Proposes a modified statement when the original is unprovable but fixable. Use when agent-prove or agent-fix determines the statement needs stronger premises or weaker conclusion. Records the proposal for orchestrator decision.
---

# Propose Statement Modification

Proposes a modified version of a statement when the original is unprovable but could be fixed.

## Workflow

1. **Update the statement** to set `status = "needs_modification"` and record the proposal
2. **If called from fix agent**: Also record the response in `validation.responses`

## Parameters Required

From the agent:
- `statement_id`: The statement to modify (e.g., `s-001`)
- `modification_type`: One of: `strengthen_premises`, `weaken_conclusion`, `add_condition`
- `suggested_claim`: The revised claim (if modified)
- `suggested_premises`: The revised premises (if modified)
- `rationale`: Why this modification is needed
- `source`: "prove" or "fix" (which agent called this)
- `issue_number`: (optional, for fix agent) Which issue revealed this

## Sample Commands

### When called from agent-prove (strengthen premises)

```bash
venv-python src/state.py \
  --id s-001 \
  --status needs_modification \
  --progresses Append "MODIFICATION PROPOSED: Type=strengthen_premises | Add hypothesis: [a,b] is compact. | Rationale: Continuity alone insufficient for max attainment; need compactness."
```

Output: `Updated s-001 [progresses,status] (log: log-XXX)`

### When called from agent-prove (weaken conclusion)

```bash
venv-python src/state.py \
  --id s-001 \
  --status needs_modification \
  --progresses Append "MODIFICATION PROPOSED: Type=weaken_conclusion | Change: 'f attains maximum' -> 'f is bounded above'. | Rationale: Without compactness, can only prove boundedness."
```

Output: `Updated s-001 [progresses,status] (log: log-XXX)`

### When called from agent-fix (with validation tracking)

```bash
venv-python src/state.py \
  --id s-001 \
  --status needs_modification \
  --progresses Append "MODIFICATION PROPOSED: Type=add_condition | Add: 'f is bounded'. | Rationale: Gap at sentence 3 requires boundedness assumption." \
  --validation.responses Append "[Response #1] Fixes Issue #1 | Type: modification | ModType: add_condition | Proposal: Add boundedness assumption."
```

Output: `Updated s-001 [progresses,status,validation] (log: log-XXX)`

### Response format structure (for fix agent)

```
[Response #N] Fixes Issue #M | Type: modification | ModType: <type> | Proposal: <summary>
```

## Output Format

### From agent-prove:
```
MODIFICATION PROPOSED: Statement [statement_id]
Original claim: [claim]
Proposed fix: [strengthen premises / weaken conclusion / add condition]
Suggestion: [the modified statement]
Rationale: [why this fixes the issue]
```

### From agent-fix:
```
MODIFICATION NEEDED: Statement [statement_id]
Issue #[N] addressed: [issue description]
Gap location: Sentence [M]
Issue: [what's wrong]
Proposed fix: [strengthen premises / weaken conclusion / add condition]
Suggestion: [the modified statement]
Validation history: [X] issues, [X] responses (proposal pending)
Status: Awaiting orchestrator decision
```

## Modification Types

- `strengthen_premises`: Add missing hypothesis
- `weaken_conclusion`: Relax the claim to something provable
- `add_condition`: Add edge case handling or extra conditions

## Notes

- The orchestrator will decide whether to accept, reject, or escalate
- Original claim/premises are preserved for reference in progresses
- A modified statement may need to be re-created as a new statement
- Common fixes:
  - Add compactness, continuity, or boundedness assumptions
  - Change strict inequalities to non-strict
  - Add "for all x satisfying [condition]" qualifiers
