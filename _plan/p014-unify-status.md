# Unify the status

## Candidates
1. Problem:
- "unresolved" (default)
- "resolved" (complete signal)
2. Problem:
- "pending" (default)
- "validating"
- "true"
- "false"
- "abandoned": one that is beyond the scope or determined to be no longer needed.

**Note** 
- Remove any other status currently in the skills files.
- When fixing the skills, please note: if creating sub-problems or sub-statements, the statement id of the new object should be added to the `preliminaries` property of the old.
- Check the script `current.py` for what to be displayed. Make sure the skills have guides align with this. (Especiall the progresses field.)


## Possibly involved files:
- All skill files in `.claude/skills/`
- Agent files in `/claude/agents/`
- Orchestrator file in `_archive/solver/`

---

# Implementation Plan

## 1. Unified Status Values

### Problem Status
| Status | Meaning |
|--------|---------|
| `unresolved` | Default. Problem needs work. |
| `resolved` | Complete. Objective achieved via proved statement(s). |

### Statement Status
| Status | Meaning |
|--------|---------|
| `pending` | Default. Statement needs proof. |
| `validating` | Proof submitted OR has issues/responses being processed. |
| `true` | Verified. Can be cited as lemma. |
| `false` | Counterexample found. Cannot be proved. |
| `abandoned` | Beyond scope OR no longer needed (parent resolved by alternative). |

### Status Transitions

```
Statement Flow:
pending → validating → true
                    ↘ false
                    ↘ abandoned

Problem Flow:
unresolved → resolved
```

---

## 2. Mapping Old Status to New

### Statuses to Replace

| Old Status | New Status | Notes |
|------------|------------|-------|
| `solved` | `resolved` | Problem completion |
| `awaiting_verification` | `validating` | After proof submitted |
| `has_gap` | `validating` | Gap found, needs fix |
| `awaiting_substatements` | `validating` | Decomposed, subs pending |
| `awaiting_substatement` | `validating` | Sub-statement for gap |
| `needs_modification` | `validating` | Modification proposed |

### Statuses to Keep As-Is
- `unresolved` (problem default)
- `pending` (statement default)
- `true` (verified)
- `false` (counterexample)

### New Status to Add
- `abandoned` (statement only)

---

## 3. Files to Modify

### Skills (11 files in `.claude/skills/`)

| Skill | Changes Needed |
|-------|----------------|
| `prob-finish-up` | Change `solved` → `resolved` |
| `prob-setup-subgoal` | Keep `unresolved` (correct) |
| `prob-wrapup-statement` | Keep `pending` (correct) |
| `state-complete-proof` | Change `awaiting_verification` → `validating` |
| `state-setup-substatement` | Change `awaiting_substatements` → `validating` |
| `state-mark-false` | Keep `false` (correct) |
| `state-propose-modification` | Change `needs_modification` → `validating` |
| `check-confirm-proof` | Keep `true` (correct) |
| `check-reject-proof` | Change `has_gap` → `validating` |
| `fix-patch-proof` | Change `awaiting_verification` → `validating` |
| `fix-create-substatement` | Change `awaiting_substatement` → `validating` |

### Agents (4 files in `.claude/agents/`)

| Agent | Changes Needed |
|-------|----------------|
| `agent-solve.md` | Update status references in workflow |
| `agent-prove.md` | Update status references in workflow |
| `agent-check.md` | Update status references in workflow |
| `agent-fix.md` | Update status references in workflow |

### Orchestrator (1 file in `_archive/solver/`)

| File | Changes Needed |
|------|----------------|
| `CLAUDE.md` | Change `solved` → `resolved` in success condition and status table |

---

## 4. Detailed Changes Per Skill

### 4.1 `prob-finish-up/SKILL.md`
**Status changes:**
- Line 3: description - change "status to solved" to "status to resolved"
- Line 13: change `status = "solved"` to `status = "resolved"`
- Line 29, 41: change `--status solved` to `--status resolved`
- Line 34, 47: update output example

### 4.2 `prob-wrapup-statement/SKILL.md`
**Progresses changes:**
- Update sample command to use format: `(s-XXX) [claim summary]`
- Change: `--progresses Append "s-XXX"` to `--progresses Append "(s-XXX) [claim summary]"`

### 4.3 `state-complete-proof/SKILL.md`
**Status changes:**
- Line 3: description - change "awaiting_verification" to "validating"
- Line 12: change `status to awaiting_verification` to `status to validating`
- Line 30, 41: change `--status awaiting_verification` to `--status validating`

**Progresses changes:**
- Add `--progresses Append "PROOF: [strategy] proof submitted, [N] steps"` to sample commands

### 4.4 `state-setup-substatement/SKILL.md`
**Status changes:**
- Line 15: change `awaiting_substatements` to `validating`
- Line 52: change `--status awaiting_substatements` to `--status validating`
- Line 75: update note about parent status

**Progresses changes:**
- Add `--progresses Append "DECOMPOSED: Created [sub-IDs]"` to sample commands

### 4.5 `state-propose-modification/SKILL.md`
**Status changes:**
- Line 12: change `needs_modification` to `validating`
- Line 33, 44, 55: change `--status needs_modification` to `--status validating`

**Progresses changes:**
- Already uses `MODIFICATION PROPOSED:` prefix - change to `MODIFICATION:` for consistency

### 4.6 `check-reject-proof/SKILL.md`
**Status changes:**
- Line 3: description - change "has_gap" to "validating"
- Line 13: change `has_gap` to `validating`
- Line 34: change `--status has_gap` to `--status validating`

### 4.7 `check-confirm-proof/SKILL.md`
**Progresses changes:**
- Already uses `Verified:` - change to `VERIFIED:` for consistency (uppercase prefix)

### 4.8 `fix-patch-proof/SKILL.md`
**Status changes:**
- Line 14: change `awaiting_verification` to `validating`
- Line 31: change `--status awaiting_verification` to `--status validating`

### 4.9 `fix-create-substatement/SKILL.md`
**Status changes:**
- Line 15: change `awaiting_substatement` to `validating`
- Line 45: change `--status awaiting_substatement` to `--status validating`
- Line 83: update note about parent status

---

## 5. Orchestrator Updates

### `_archive/solver/CLAUDE.md`

**Success Condition section:**
- Change `status == "solved"` → `status == "resolved"`

**Status table updates:**
| Old | New |
|-----|-----|
| `solved` | `resolved` |
| `awaiting_verification` | `validating` |
| `has_gap` | `validating` |
| `awaiting_substatements` | `validating` |
| `awaiting_substatement` | `validating` |

Add `abandoned` to status table.

---

## 6. Progresses Field Usage

Per `current.py`, the `progresses` field is displayed for both problems and statements as a simple list. Each entry is shown as `- {text}`.

**Brevity Rule**: Each progresses entry should be brief — no more than 2 sentences.

### 6.1 Problem Progresses

**Format**: `(s-XXX) [brief description of what the statement proves]`

**Example**:
```
--progresses Append "(s-001) proves f attains maximum on [a,b]"
```

**When to add**:
- `prob-wrapup-statement`: When creating a statement to resolve the problem
- `prob-finish-up`: When recording final resolution

### 6.2 Statement Progresses

**Use standardized prefixes** to identify entry type:

| Prefix | When Used | Example |
|--------|-----------|---------|
| `COUNTEREXAMPLE:` | `state-mark-false` | `COUNTEREXAMPLE: f(x)=x on [0,1] has max=1` |
| `MODIFICATION:` | `state-propose-modification` | `MODIFICATION: Add hypothesis [a,b] compact` |
| `VERIFIED:` | `check-confirm-proof` | `VERIFIED: 5 steps checked, all valid` |
| `PROOF:` | `state-complete-proof` | `PROOF: Direct proof submitted, 4 steps` |
| `DECOMPOSED:` | `state-setup-substatement` | `DECOMPOSED: Created s-002, s-003` |

**Skills to update for progresses**:
- `prob-wrapup-statement`: Change from just `s-XXX` to `(s-XXX) [claim summary]`
- `state-complete-proof`: Add `PROOF:` entry when submitting
- `state-setup-substatement`: Add `DECOMPOSED:` entry listing sub-statement IDs

This aligns with the simplified status model where `validating` covers multiple sub-states, and `progresses` provides human-readable context.

---

## 7. Validation Field Usage

For statements in `validating` status, the `validation` field tracks:
- `issues`: List of gaps/problems found by checker
- `responses`: List of fixes applied by fixer

The relationship `len(issues) vs len(responses)` determines the sub-state:
- `issues > responses`: Unresolved issues, needs agent-fix
- `issues == responses`: All addressed, needs agent-check re-verification

This is already implemented in `current.py` and should be maintained.

---

## 8. Preliminaries Field Usage

When creating sub-problems or sub-statements:
- Add the new object's ID to the parent's `preliminaries` list
- This is already specified in most skills but should be verified

Skills affected:
- `prob-setup-subgoal`: Add subproblem ID to parent's preliminaries ✓
- `state-setup-substatement`: Add sub-statement IDs to parent's preliminaries ✓
- `fix-create-substatement`: Add sub-statement ID to parent's preliminaries ✓

---

## 9. Implementation Order

1. **Phase 1**: Update skill files (11 files)
2. **Phase 2**: Update agent files (4 files)
3. **Phase 3**: Update orchestrator file (1 file)
4. **Phase 4**: Verify `current.py` alignment (no changes expected)

---

## 10. Verification Checklist

After implementation:

**Status values:**
- [ ] All skills use only: `unresolved`, `resolved`, `pending`, `validating`, `true`, `false`, `abandoned`
- [ ] No occurrences of deprecated statuses: `solved`, `awaiting_verification`, `has_gap`, `awaiting_substatements`, `awaiting_substatement`, `needs_modification`
- [ ] Orchestrator success condition uses `resolved`
- [ ] Orchestrator status table matches new values

**Progresses field:**
- [ ] Problem progresses use format: `(s-XXX) [claim summary]`
- [ ] Statement progresses use uppercase prefixes: `COUNTEREXAMPLE:`, `MODIFICATION:`, `VERIFIED:`, `PROOF:`, `DECOMPOSED:`
- [ ] `prob-wrapup-statement` includes claim summary in progresses entry
- [ ] `state-complete-proof` adds `PROOF:` entry
- [ ] `state-setup-substatement` adds `DECOMPOSED:` entry

**Preliminaries field:**
- [ ] Skills correctly use `preliminaries` for sub-object linking

---

## 11. Summary of All Changes

| File | Status Changes | Progresses Changes |
|------|----------------|-------------------|
| `prob-finish-up` | `solved` -> `resolved` | - |
| `prob-wrapup-statement` | - | Add `(s-XXX) [summary]` format |
| `state-complete-proof` | `awaiting_verification` -> `validating` | Add `PROOF:` entry |
| `state-setup-substatement` | `awaiting_substatements` -> `validating` | Add `DECOMPOSED:` entry |
| `state-propose-modification` | `needs_modification` -> `validating` | Change to `MODIFICATION:` prefix |
| `state-mark-false` | - | Keep `COUNTEREXAMPLE:` (already correct) |
| `check-confirm-proof` | - | Change to `VERIFIED:` (uppercase) |
| `check-reject-proof` | `has_gap` -> `validating` | - |
| `fix-patch-proof` | `awaiting_verification` -> `validating` | - |
| `fix-create-substatement` | `awaiting_substatement` -> `validating` | - |
| `prob-setup-subgoal` | - (already `unresolved`) | - |
| Orchestrator | `solved` -> `resolved` | - |