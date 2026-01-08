# P013: Write Skills for Agent System

## Overview

This plan covers the creation of all skills referenced by the four agents (agent-solve, agent-prove, agent-check, agent-fix). Skills are invoked by agents to perform JSON file operations via Python scripts.

## Skill Architecture

Each skill consists of:
1. **Skill definition file** (`.claude/skills/<skill-name>.md`) — Instructions for the agent
2. **Python script** (`src/skills/<skill_name>.py`) — Actual JSON manipulation logic

Skills communicate via:
- **Input**: Agent provides parameters when loading the skill
- **Output**: Script modifies JSON files and returns confirmation

---

## Consolidated Skill List

After merging overlapping skills:
- `state-mark-false` + `fix-mark-false` → **`state-mark-false`** (unified)
- `state-propose-modification` + `fix-propose-modification` → **`state-propose-modification`** (unified)

### Final Skills (11 total)

| # | Skill Name | Agent(s) | Purpose |
|---|------------|----------|---------|
| 1 | `prob-finish-up` | agent-solve | Mark problem as solved |
| 2 | `prob-setup-subgoal` | agent-solve | Create subproblem |
| 3 | `prob-wrapup-statement` | agent-solve | Create statement to resolve problem |
| 4 | `state-complete-proof` | agent-prove | Submit proof for verification |
| 5 | `state-setup-substatement` | agent-prove, agent-fix | Create sub-statement(s) |
| 6 | `state-mark-false` | agent-prove, agent-fix | Mark statement as false with counterexample |
| 7 | `state-propose-modification` | agent-prove, agent-fix | Propose modified statement |
| 8 | `check-confirm-proof` | agent-check | Confirm proof valid, set status="true" |
| 9 | `check-reject-proof` | agent-check | Record gap in validate.issues |
| 10 | `fix-patch-proof` | agent-fix | Apply direct fix to proof text |
| 11 | `fix-create-substatement` | agent-fix | Create sub-statement to fill gap (with validation tracking) |

---

## Development Checklist

### Problem Skills (agent-solve)

- [x] **1. `prob-finish-up`** *(completed)*

  **Purpose**: Mark a problem as solved after a key statement has been proved.

  **Input parameters**:
  - `problem_path`: Path to the problem JSON file
  - `resolution`: Text explaining how the objective follows from the proved statement
  - `key_statement_id`: ID of the statement (with status="true") that enables resolution

  **Actions**:
  - Set `problem.status = "solved"`
  - Set `problem.resolution = resolution`
  - Set `problem.resolved_by = key_statement_id`
  - Record timestamp

  **Output**: Confirmation message with problem ID

---

- [x] **2. `prob-setup-subgoal`** *(completed)*

  **Purpose**: Create a new subproblem when the current problem is too complex.

  **Input parameters**:
  - `parent_problem_path`: Path to the parent problem JSON
  - `subproblem_objective`: What the subproblem should prove
  - `subproblem_hypothesis`: Conditions inherited or specified for subproblem
  - `rationale`: Why this decomposition helps

  **Actions**:
  - Generate unique subproblem ID (e.g., `prob_<parent>_sub<N>`)
  - Create new problem JSON in `contents/problem/`
  - Initialize: `status = "pending"`, `parent = parent_id`
  - Update parent's `preliminaries` list to include subproblem ID

  **Output**: New subproblem ID and path

---

- [x] **3. `prob-wrapup-statement`** *(completed)*

  **Purpose**: Create a statement that, once proved, resolves the problem.

  **Input parameters**:
  - `problem_path`: Path to the problem JSON
  - `claim`: The precise statement to be proved
  - `premises`: Conditions assumed true for this statement
  - `purpose`: How this statement completes the problem resolution

  **Actions**:
  - Generate unique statement ID (e.g., `stmt_<problem>_wrap`)
  - Create new statement JSON in `contents/statement/`
  - Initialize: `status = "pending"`, `context = problem_id`
  - Update problem's `progresses` list to include statement ID

  **Output**: New statement ID and path

---

### Statement Skills (agent-prove)

- [x] **4. `state-complete-proof`** *(completed)*

  **Purpose**: Submit a completed proof for verification.

  **Input parameters**:
  - `statement_path`: Path to the statement JSON
  - `proof_text`: The complete proof (structured with steps)
  - `strategy`: Proof strategy used (direct/contradiction/case_analysis/backward)

  **Actions**:
  - Set `statement.proof = proof_text`
  - Set `statement.proof_strategy = strategy`
  - Set `statement.status = "awaiting_verification"`
  - Initialize `statement.validate = {"issues": [], "responses": []}` if not exists

  **Output**: Confirmation, statement ready for agent-check

---

- [x] **5. `state-setup-substatement`** *(completed)*

  **Purpose**: Decompose a statement into simpler sub-statements.

  **Input parameters**:
  - `parent_statement_path`: Path to the parent statement JSON
  - `sub_statements`: List of {claim, premises} objects
  - `rationale`: Why this decomposition helps

  **Actions**:
  - For each sub-statement:
    - Generate unique ID (e.g., `stmt_<parent>_sub<N>`)
    - Create new statement JSON in `contents/statement/`
    - Initialize: `status = "pending"`, `context = parent_statement_id`
  - Update parent's `sub_statements` list
  - Set parent `status = "awaiting_substatements"`

  **Output**: List of new sub-statement IDs and paths

---

- [x] **6. `state-mark-false`** (unified) *(completed)*

  **Purpose**: Mark a statement as false when a counterexample is found.

  **Used by**: agent-prove (during proof attempt), agent-fix (during gap analysis)

  **Input parameters**:
  - `statement_path`: Path to the statement JSON
  - `counterexample`: Description of the counterexample
  - `source`: "prove" or "fix" (which agent called this)
  - `issue_number`: (optional, for fix agent) Which issue revealed this

  **Actions**:
  - Set `statement.status = "false"`
  - Set `statement.counterexample = counterexample`
  - If called from fix agent:
    - Append to `validate.responses`: `{type: "false", issue_addressed: N, counterexample: ...}`
  - Record timestamp and source

  **Output**: Confirmation, note about parent impact

---

- [x] **7. `state-propose-modification`** (unified) *(completed)*

  **Purpose**: Propose a modified statement when the original is unprovable but fixable.

  **Used by**: agent-prove (during proof attempt), agent-fix (during gap analysis)

  **Input parameters**:
  - `statement_path`: Path to the statement JSON
  - `modification_type`: "strengthen_premises" | "weaken_conclusion" | "add_condition"
  - `suggested_claim`: The revised claim (if modified)
  - `suggested_premises`: The revised premises (if modified)
  - `rationale`: Why this modification is needed
  - `source`: "prove" or "fix"
  - `issue_number`: (optional, for fix agent) Which issue revealed this

  **Actions**:
  - Set `statement.status = "needs_modification"`
  - Set `statement.proposed_modification = {type, claim, premises, rationale}`
  - If called from fix agent:
    - Append to `validate.responses`: `{type: "modification", issue_addressed: N, proposal: ...}`
  - Preserve original claim/premises for reference

  **Output**: Confirmation, awaiting orchestrator decision

---

### Check Skills (agent-check)

- [x] **8. `check-confirm-proof`** *(completed)*

  **Purpose**: Confirm that a proof is valid and mark the statement as true.

  **Input parameters**:
  - `statement_path`: Path to the statement JSON
  - `verification_summary`: Brief summary of verification (steps checked, etc.)

  **Actions**:
  - Set `statement.status = "true"`
  - Set `statement.verified_at = timestamp`
  - Optionally: Set `statement.verification_summary = summary`

  **Output**: Confirmation message

---

- [x] **9. `check-reject-proof`** *(completed)*

  **Purpose**: Record a gap found during proof verification.

  **Input parameters**:
  - `statement_path`: Path to the statement JSON
  - `sentence_number`: Which sentence has the gap
  - `sentence_text`: The exact text of the problematic sentence
  - `error_type`: "gap" | "unjustified_leap" | "hidden_assumption" | "circular" | "scope_error" | "wrong_target"
  - `explanation`: Detailed description of what's wrong
  - `suggested_fix`: What would be needed to fix this

  **Actions**:
  - Append to `statement.validate.issues[]`:
    ```json
    {
      "issue_number": <auto-increment>,
      "sentence": <sentence_number>,
      "sentence_text": "<text>",
      "error_type": "<type>",
      "explanation": "<explanation>",
      "suggested_fix": "<suggestion>",
      "created_at": "<timestamp>"
    }
    ```
  - Set `statement.status = "has_gap"`

  **Output**: Issue number assigned

---

### Fix Skills (agent-fix)

- [x] **10. `fix-patch-proof`** *(completed)*

  **Purpose**: Apply a direct fix to the proof text.

  **Input parameters**:
  - `statement_path`: Path to the statement JSON
  - `issue_number`: Which issue this fixes
  - `sentence_range`: {start: N, end: M} — sentences to replace
  - `replacement_text`: The new proof text for that range
  - `change_description`: Brief description of what was changed

  **Actions**:
  - Parse `statement.proof` into sentences
  - Replace sentences [start, end] with replacement_text
  - Reconstruct proof
  - Append to `statement.validate.responses[]`:
    ```json
    {
      "response_number": <auto-increment>,
      "issue_addressed": <issue_number>,
      "type": "patch",
      "sentence_range": {start, end},
      "change_description": "<description>",
      "created_at": "<timestamp>"
    }
    ```
  - Set `statement.status = "awaiting_verification"`

  **Output**: Confirmation, proof updated

---

- [x] **11. `fix-create-substatement`** *(completed)*

  **Purpose**: Create a sub-statement to fill a gap, with validation tracking.

  **Input parameters**:
  - `statement_path`: Path to the statement JSON
  - `issue_number`: Which issue this addresses
  - `sub_claim`: The claim for the sub-statement
  - `sub_premises`: Premises for the sub-statement
  - `gap_location`: Which sentence the sub-statement will support
  - `purpose`: How this sub-statement fills the gap

  **Actions**:
  - Generate unique ID (e.g., `stmt_<parent>_fix<N>`)
  - Create new statement JSON in `contents/statement/`
  - Initialize: `status = "pending"`, `context = parent_statement_id`, `fills_gap_at = gap_location`
  - Update parent's `sub_statements` list
  - Append to `statement.validate.responses[]`:
    ```json
    {
      "response_number": <auto-increment>,
      "issue_addressed": <issue_number>,
      "type": "substatement",
      "sub_statement_id": "<new_id>",
      "purpose": "<purpose>",
      "created_at": "<timestamp>"
    }
    ```
  - Set parent `statement.status = "awaiting_substatement"`

  **Output**: New sub-statement ID and path

---

## Implementation Order (Suggested)

### Phase 1: Core Problem/Statement Creation
1. `prob-wrapup-statement` — Most fundamental: creates statements from problems
2. `state-complete-proof` — Submit proofs
3. `check-confirm-proof` — Verify and mark true
4. `prob-finish-up` — Close solved problems

### Phase 2: Decomposition
5. `prob-setup-subgoal` — Problem decomposition
6. `state-setup-substatement` — Statement decomposition

### Phase 3: Validation Loop
7. `check-reject-proof` — Record gaps
8. `fix-patch-proof` — Direct fixes
9. `fix-create-substatement` — Gap-filling sub-statements

### Phase 4: Edge Cases
10. `state-mark-false` — Handle false statements
11. `state-propose-modification` — Handle fixable statements

---

## File Structure (To Be Created)

```
.claude/skills/
├── prob-finish-up.md
├── prob-setup-subgoal.md
├── prob-wrapup-statement.md
├── state-complete-proof.md
├── state-setup-substatement.md
├── state-mark-false.md
├── state-propose-modification.md
├── check-confirm-proof.md
├── check-reject-proof.md
├── fix-patch-proof.md
└── fix-create-substatement.md

src/skills/
├── prob_finish_up.py
├── prob_setup_subgoal.py
├── prob_wrapup_statement.py
├── state_complete_proof.py
├── state_setup_substatement.py
├── state_mark_false.py
├── state_propose_modification.py
├── check_confirm_proof.py
├── check_reject_proof.py
├── fix_patch_proof.py
└── fix_create_substatement.py
```

---

## Notes

- All Python scripts should use the existing `src/state.py` and `src/prob.py` utilities where applicable
- Each skill should validate inputs before modifying files
- All modifications should be atomic (complete or rollback)
- Timestamps should use ISO 8601 format
- IDs should be deterministic and traceable to parent entities

---

## Status

**Created**: 2026-01-08
**Status**: COMPLETED - All 11 skills created

### Completed Skills

All skills have been created in `.claude/skills/` with their own subfolders:

1. `prob-wrapup-statement/SKILL.md` - Creates statement to resolve problem
2. `state-complete-proof/SKILL.md` - Submits proof for verification
3. `check-confirm-proof/SKILL.md` - Confirms valid proof
4. `prob-finish-up/SKILL.md` - Marks problem as solved
5. `prob-setup-subgoal/SKILL.md` - Creates subproblem
6. `state-setup-substatement/SKILL.md` - Creates sub-statements
7. `check-reject-proof/SKILL.md` - Records proof gap
8. `fix-patch-proof/SKILL.md` - Applies direct fix
9. `fix-create-substatement/SKILL.md` - Creates sub-statement to fill gap
10. `state-mark-false/SKILL.md` - Marks statement as false
11. `state-propose-modification/SKILL.md` - Proposes statement modification
