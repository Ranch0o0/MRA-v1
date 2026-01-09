---
name: prob-core-statement
description: Creates a statement that resolves a problem. Use when agent-solve determines a single statement can bridge the gap between hypothesis and objective. Invokes src/state.py to create the statement and src/prob.py to link it.
---

# Create core Statement for Problem

Creates a set new statements that, once proved, resolves the problem objective.

## Workflow

1. **Create the statement(s)** using `src/state.py`
2. **Link to problem** by updating the problem's `progresses` list using `src/prob.py`

## Parameters Required

From the agent:
- `problem_id`: The problem to resolve (e.g., `p-001`)
- `claim`: The precise statement to be proved (list of strings)
- `premises`: Conditions assumed true for this statement (list of strings)
- `purpose`: How this statement completes the problem resolution

## Principles for claim:
- No wrap up. The claim should be direct to the core fact, and no wrap-ups.
- Atomic. The claim should be indecomposible. In case of decomposible, **Create multiple statements instead of one**
<example>
<wrong>The solution to the problem is {{A}} and {{B}}</wrong>
<correct-action>Create two statements, one for A and one for B</correct-action>
</example>

 **Note** In case of multiple statement, run `src/state.py` multiple times, and create one statement per run.

## Sample Commands

### Step 1: Create the statement(s)

```bash
venv-python src/state.py \
  --type normal \
  --conclusion "If f is continuous on [a,b] then f attains its maximum" \
  --hypothesis Overwrite "f is continuous on [a,b]" "[a,b] is a closed bounded interval"
```

Output: `Created statement: s-XXX`

**May run this step multiple times to create multiple statements**

### Step 2: Link statement to problem's progresses

Use format: `(s-XXX) ... (s-YYY) [brief claim summary]` (max 2 sentences)

```bash
venv-python src/prob.py \
  --id p-001 \
  --progresses Append "(s-XXX) ... (s-YYY) altogether prove f attains maximum on [a,b]"
```

Output: `Updated p-001 [progresses] (log: log-XXX)`

## Output Format

Report to orchestrator:
```
STATEMENT CREATED: Problem [problem_id] -> Statement [statement_id]
Claim: [the claim]
Purpose: [how this resolves the problem]
Status: Statement awaiting proof by agent-prove
```

## Notes

- Statement is created with `status = "pending"` and `type = "normal"`
- The claim should be precise enough for agent-prove to prove directly
- Premises should include all conditions needed from the problem's hypothesis
- If adding a currently existing statement to the hypothesis, include its id in the form: `({{statement_id}}) {{statement_content}}`
