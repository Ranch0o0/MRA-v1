---
name: state-setup-substatement
description: Decomposes a statement into simpler sub-statements. Use when agent-prove or agent-fix determines the proof requires intermediate lemmas. Creates child statements and links them to parent's preliminaries.
---

# Create Sub-statements

Decomposes a statement into simpler sub-statements for recursive proving.

## Workflow

For each sub-statement:
1. **Create the sub-statement** using `src/state.py`
2. **Link to parent** by updating the parent's `preliminaries` list
3. **Update parent status** to `validating`
4. **Record progress** with `DECOMPOSED:` prefix (max 2 sentences)

## Parameters Required

From the agent:
- `parent_statement_id`: The parent statement (e.g., `s-001`)
- `sub_statements`: List of {claim, premises} for each sub-statement
- `rationale`: Why this decomposition helps

## Sample Commands

### Step 1: Create each sub-statement

```bash
venv-python src/state.py \
  --type normal \
  --conclusion "f attains its supremum on [a,b]" \
  --hypothesis Overwrite "f is continuous" "[a,b] is compact"
```

Output: `Created statement: s-XXX`

```bash
venv-python src/state.py \
  --type normal \
  --conclusion "[a,b] is compact" \
  --hypothesis Overwrite "[a,b] is closed and bounded in R"
```

Output: `Created statement: s-YYY`
**Note** 
1. Run the scrip `src/state.py` multiple times, one for each substatement to be created.
2. **Note**
When adding exisitng conclusions as hypothesis, can only include the statement id: `--hypothesis Overwrite "(s-xxx)"`.

### Step 2: Link sub-statements to parent's preliminaries

```bash
venv-python src/state.py \
  --id s-001 \
  --preliminaries Append "s-XXX" "s-YYY" \
  --status validating \
  --progresses Append "DECOMPOSED: Created s-XXX, s-YYY"
```

Output: `Updated s-001 [preliminaries,progresses,status] (log: log-XXX)`

## Output Format

Report to orchestrator:
```
DECOMPOSED: Statement [parent_id]
Created [N] sub-statement(s):
- Sub-statement [s-XXX]: [brief claim]
- Sub-statement [s-YYY]: [brief claim]
Rationale: [why this decomposition helps]
Status: Sub-statements awaiting proof
```

## Notes

- Each sub-statement is created with `status = "pending"` and `type = "normal"`
- Sub-statements should be strictly simpler than the parent
- Together, the sub-statements must be sufficient to prove the parent
- Avoid redundant sub-statements
- The parent's status changes to `validating`
- If adding a currently existing statement to the hypothesis, include its id in the form: `({{statement_id}}) {{statement_content}}`
