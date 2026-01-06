# Refine Script Feedback

## Meta Info
- **Scripts to change**: `src/prob_init.py`, `src/prob.py`, `src/state.py`
- **Goal**: Improve terminal output clarity while maintaining conciseness

## Current State

| Script | Operation | Current Output |
|--------|-----------|----------------|
| `prob_init.py` | Create initial problem | `Created initial problem: p-001` |
| `prob.py` | Create problem | `Created problem: p-002` |
| `prob.py` | Update problem | `Updated problem p-002 (log: l-006)` |
| `state.py` | Create statement | `Created statement: s-014` |
| `state.py` | Update statement | `Updated statement s-014 (log: l-005)` |

## Evaluation

### Strengths
- Single-line outputs (very compact)
- Essential info: operation type + ID + log ID
- No verbose descriptions

### Weaknesses
1. **Missing nested object info**: When creating problems with hypothesis items, nested statements are created but not reported
2. **No field summary for updates**: Agent doesn't know which fields were actually modified

## Proposed Changes

### 1. `prob_init.py` - Add nested statement count
```
# Current:
Created initial problem: p-001

# Proposed:
Created initial problem: p-001 [+13 statements]
```

### 2. `prob.py` - Add nested info and update fields

**Create mode:**
```
# Current:
Created problem: p-002

# Proposed (with nested statements):
Created problem: p-002 [+2 statements]

# Proposed (no nested statements):
Created problem: p-002
```

**Update mode:**
```
# Current:
Updated problem p-002 (log: l-006)

# Proposed:
Updated p-002 [status,summary,solution] (log: l-006)
```

### 3. `state.py` - Add update fields

**Create mode:** (no change needed - already clear)
```
Created statement: s-014
```

**Update mode:**
```
# Current:
Updated statement s-014 (log: l-005)

# Proposed:
Updated s-014 [status,reliability,proof] (log: l-005)
```

## Implementation Details

### Format Specifications
- Nested creations: `[+N statements]` or `[+N objects]`
- Updated fields: `[field1,field2,field3]` (comma-separated, no spaces)
- Keep log ID in parentheses for updates
- Maximum field list: show up to 4 fields, then `...` if more

### Field Name Mapping
For updates, use short field names:
- `status` → `status`
- `summary` → `summary`
- `priority` → `priority`
- `progresses` → `progresses`
- `preliminaries` → `preliminaries`
- `solution.cot` → `solution`
- `solution.full` → `solution`
- `solution.ref` → `solution`
- `proof.cot` → `proof`
- `proof.full` → `proof`
- `proof.ref` → `proof`
- `reliability` → `reliability`
- `hypothesis` → `hypothesis`
- `conclusion` → `conclusion`

Note: Group nested fields (e.g., all `solution.*` fields show as single `solution`)

## Implementation Steps

1. **Update `prob_init.py`**
   - Count nested statement creations from the changes list
   - Modify print statement to include count

2. **Update `prob.py`**
   - For create mode: count nested statements and include in output
   - For update mode: extract field names from updates dict and format

3. **Update `state.py`**
   - For update mode: extract field names from updates dict and format

4. **Helper function** (optional)
   - Consider adding a `format_field_list(updates: dict) -> str` helper in each script
   - Groups nested fields (solution.*, proof.*) into single names
