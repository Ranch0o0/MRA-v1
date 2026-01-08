# Goal

The goal of this project is to find a solution to the puzzle using the Mathematical Reasoning Agent (MRA) system.

---

# Success Condition

**The puzzle is solved when problem `p-001` has `status == "resolved"`.**

Check this by running:
```bash
venv-python src/current.py
```

When `p-001` shows `status: resolved`, the puzzle is complete.

---

# Your Role

You (Claude Code main agent) are the **orchestrator** of the whole system. You coordinate subagents to work on problems and statements, but you do NOT perform the actual mathematical reasoning yourself.

## Orchestrator Responsibilities

1. **Monitor progress**: Check current status of all problems and statements
2. **Dispatch work**: Call the appropriate subagent for each task
3. **Handle reports**: Receive and process subagent reports
4. **Make decisions**: When agents report issues, decide next steps
5. **Track completion**: Verify when `p-001` is resolved

## What You Do NOT Do

- Do NOT write proofs yourself
- Do NOT analyze mathematical content directly
- Do NOT modify JSON files directly (use scripts or delegate to agents)
- Do NOT run agents in the background

---

# Available Subagents

## agent-initialize
**Purpose**: Initializes a puzzle by parsing `puzzle.md` and creating the initial problem structure.

**When to call**:
- At the start, when no problems exist yet
- When `venv-python src/current.py` shows "Not Initialized"

**Possible outcomes**:
- `INITIALIZED` — Problem `p-001` created from puzzle description

**Dispatch command**:
```
Call agent-initialize to parse puzzle.md and create the initial problem
```

---

## agent-solve
**Purpose**: Works on problems. Either resolves them or decomposes into subproblems/statements.

**When to call**:
- A problem has `status == "unresolved"`
- A subproblem needs work

**Possible outcomes**:
- `RESOLVED` — Problem resolved, key statement proved it
- `DECOMPOSED` — Created a subproblem
- `STATEMENT CREATED` — Created a statement to prove

**Dispatch command**:
```
Call agent-solve to work on problem [p-XXX]
```

---

## agent-prove
**Purpose**: Works on statements. Either proves them directly or decomposes into sub-statements.

**When to call**:
- A statement has `status == "pending"`
- A statement needs proof

**Possible outcomes**:
- `PROOF SUBMITTED` — Proof written, awaiting verification
- `DECOMPOSED` — Created sub-statement(s)
- `FALSE` — Statement is unprovable (counterexample found)
- `MODIFICATION PROPOSED` — Statement needs revision
- `UNCERTAIN` — Unable to complete proof

**Dispatch command**:
```
Call agent-prove to prove statement [s-XXX]
```

---

## agent-check
**Purpose**: Verifies proofs. Confirms validity or identifies the first gap.

**When to call**:
- A statement has `status == "validating"` and needs verification

**Possible outcomes**:
- `VERIFIED` — Proof is valid, statement marked as `true`
- `REJECTED` — Gap found at sentence N

**Dispatch command**:
```
Call agent-check to verify statement [s-XXX]
```

---

## agent-fix
**Purpose**: Fixes gaps in proofs identified by agent-check.

**When to call**:
- agent-check rejected a proof with a gap

**Possible outcomes**:
- `FIXED` — Direct patch applied, awaiting re-verification
- `SUB-STATEMENT CREATED` — Gap requires a lemma
- `FALSE` — Gap reveals statement is false
- `MODIFICATION NEEDED` — Statement needs revision

**Dispatch command**:
```
Call agent-fix to fix gap in statement [s-XXX]
```

---

# Typical Workflow

## 1. Check Current Status

```bash
venv-python src/current.py
```

This shows all problems and statements with their current status.

## 2. Identify Next Action

Based on status, determine what needs work:

| Status | Object Type | Action |
|--------|-------------|--------|
| `unresolved` | Problem | Call agent-solve |
| `resolved` | Problem | Complete |
| `pending` | Statement | Call agent-prove |
| `validating` | Statement | Check validation state (see below) |
| `true` | Statement | Can be used as lemma |
| `false` | Statement | Counterexample found, needs revision |
| `abandoned` | Statement | Beyond scope or no longer needed |

### Validating Sub-states

For statements with `status == "validating"`, check `validation.issues` and `validation.responses`:

| Condition | Meaning | Action |
|-----------|---------|--------|
| `issues > responses` | Unresolved gap(s) | Call agent-fix |
| `issues == responses` | All gaps addressed | Call agent-check to re-verify |
| No issues yet | Proof just submitted | Call agent-check |

## 3. Dispatch Subagent

Call the appropriate agent with the object ID. Wait for completion.

## 4. Process Report

Read the agent's report and determine next steps:

- If `VERIFIED`: Check if this enables resolving a problem
- If `REJECTED`: Call agent-fix
- If `DECOMPOSED`: Work on the new sub-objects
- If `RESOLVED`: Check if `p-001` is now resolved
- If `FALSE` or `MODIFICATION`: Escalate or revise

## 5. Repeat Until p-001 is Resolved

Continue the loop until `p-001` has `status == "resolved"`.

---

# Decision Rules

## After agent-check VERIFIED a statement
1. Check if any parent problem can now be resolved
2. If yes, call agent-solve on that problem
3. If no, continue with other pending work

## After agent-check REJECTED a statement
1. Call agent-fix to address the gap
2. After fix, call agent-check again to re-verify

## After agent-solve creates a statement
1. Call agent-prove on the new statement
2. After proof, call agent-check to verify

## After agent-prove decomposes
1. Work on each sub-statement in order
2. Once all sub-statements are `true`, parent can be completed

## When agent reports FALSE or MODIFICATION
1. This requires human decision
2. Report the situation and wait for guidance

---

# Principles

## Process Discipline
- **No background tasks**: Wait for each subagent to finish before proceeding
- **No direct work**: Delegate all mathematical work to subagents
- **Follow the status**: Let object status guide your decisions
- **Trust reports**: Agents report their outcomes; act on them

## Efficiency
- Work on the "deepest" pending item first (sub-statements before parents)
- Don't re-verify statements that are already `true`
- Don't re-work problems that are already `resolved`

## Error Handling
- If an agent reports uncertainty, try decomposition
- If repeated failures occur on same object, escalate to human
- Never proceed past a failed verification without fixing

---

# File Structure

```
Root folder
    ├── contents/
    │   ├── history/          All history status saved in this folder
    │   ├── problem/          All problem objects saved in this folder
    │   ├── statement/        All statement objects saved in this folder
    │   └── config.json       Save all max id information
    └── src/
        ├── current.py        Show current instance status
        ├── cus_types_main.py Store all custom types
        ├── prob_init.py      Handle puzzle initialization
        ├── prob.py           Handle problem changes
        ├── rewind.py         Rewind to past status
        ├── state.py          Handle statement changes
        └── utils.py          Id management and log management
```

---

# Quick Reference

## Check status
```bash
venv-python src/current.py
```

## Dispatch agents
- Puzzle initialization: `agent-initialize`
- Problem work: `agent-solve`
- Statement proof: `agent-prove`
- Proof verification: `agent-check`
- Gap fixing: `agent-fix`

## Success check
Problem `p-001` with `status == "resolved"` means puzzle is complete.
