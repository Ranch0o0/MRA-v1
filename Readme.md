# Virtual environment
- **IMPORTANT** All scripts are run via virtual environment. The instructions to agents and skills hard coded the virtual environment path which may need to be replaced.
- One idea to do this is to wrap the python virtual environment by the alias `venv-python`, which is currently used in the instruction to all agents and skills.
```zsh
which venv-python
venv-python: aliased to /Users/zhenkun/Documents/Python/Virtual_environment/bin/python
```
- Or else one may need to modify the instruction to all agents and skills in `.claude/agents` and `.claude/skills`

# Quick start
0. Start Claude Code via terminal command `claude` (after installation) or via the vs code's claude code plugin.

1. To change the puzzle: manually modify `puzzle.md`.

2. To start a new test: (make sure `puzzle.md` contains the puzzle you want to test)
- Use slash command `/start`

3. To resume solving the puzzle (interrupted for any reason or rewind to some status)
- Use slash command `/resume`

4. To run the puzzle-solving process for several steps ((changes in log id))
- Use slash command `/step $ARGUMENTS`
- `$ARGUMENT` should be the number of steps you would like the claude code agent to proceed.
<example>
/step 5
</example>

5. To run the process with one step and inject human instructions:
- Use slash command `/instruct $ARGUMENTS`
- `$ARGUMENT` should include: which agent to call and what are the instructions.
<example>
/instruct agent-check: please check statement (s-010) and especially the third sentence is problematic, since the situation that spy can either tell the truth or lying seems to be overlooked.
</example>

**Important** If any slash command does not work as expected, check if global slash commands collide with project level slash commands.

6. To rewind to a past status
- Find the log id you want to rewind to.
- Modify the main block of the script `src/rewind.py`
- Run the script, and confirm in terminal.
**Caution** This is non-reversible. Use github version control if you want to go back and force or even exploring multi-branches.

# File structure
Root folder
    ├──contents
    │   ├──history              All history status saved in this folder
    │   ├──problem              All problem objects saved in this folder
    │   ├──statement            All statement objects saved in this folder
    │   └──config.json          Save all max id informations
    └──src
        ├──current.py           Show current instance status
        ├──cus_types_main.py    Store all custom types
        ├──prob_init.py         Handle puzzle initialization  
        ├──prob.py              Handle problem changes
        ├──rewind.py            Rewind to past status
        ├──state.py             Handle statement changes
        └──utils.py             Id management and log management

# System structure
This prototype has the following building blocks.

## Claude code system
1. Commands
Several commands has been included to quickly test on the puzzle.
- `/start`
- `/resume`
- `/step`
- `/instruct`

2. Agents
Several agents have been designed to handle different type of logic tasks to solve the puzzle.
- `agent-initialize`: Parses `puzzle.md` and creates the initial problem `p-001`. Called once at start.
- `agent-solve`: Works on problems. Creates statements to prove or decomposes into subproblems.
- `agent-prove`: Proves statements directly or decomposes into sub-statements.
- `agent-check`: Verifies proofs sentence-by-sentence. Confirms validity or identifies gaps.
- `agent-fix`: Fixes gaps in proofs. Patches minor issues or creates sub-statements for major gaps.

3. Skills
Several skills have been created to handle particular execution tasks involving scripts.

**Statement skills** (used by agents to update statement objects):
- `state-complete-proof`: Submit a completed proof for verification (sets status to validating).
- `state-setup-substatement`: Decompose a statement into simpler sub-statements.
- `state-mark-false`: Mark a statement as false when a counterexample is found.
- `state-propose-modification`: Propose a modified statement when original is unprovable but fixable.

**Problem skills** (used by agents to update problem objects):
- `prob-core-statement`: Create a statement that resolves a problem.
- `prob-finish-up`: Mark a problem as resolved after key statement is proved.
- `prob-setup-subgoal`: Create a subproblem when current problem is too complex.

**Verification skills** (used by agent-check and agent-fix):
- `check-confirm-proof`: Confirm a proof is valid and mark statement as true.
- `check-reject-proof`: Record a gap found during proof verification.
- `fix-patch-proof`: Apply a direct fix to proof text (minor additions, 3 or fewer steps).
- `fix-create-substatement`: Create a sub-statement to fill a gap identified by agent-check.

**Special remarks**
- The claude code system has a few building blocks: slash commands, subagents, skills, and many more (e.g. hooks, mcps). In this demo, we only use these three (as they are simple but already powerful).
- A simple principle: all three things are simply prompt/context engineering, and all three are about editing markdown files.
- Trade-off: all these three blocks (commands, agents, skills) are not hard-coded constraints for our math reasoning system. They are built upon the prompt-following capacity and large enough context window of the base model.

## Status values

### Problem status
| Status | Meaning |
|--------|---------|
| `unresolved` | Default. Problem needs work. |
| `resolved` | Complete. Objective achieved via proved statement(s). |

### Statement status
| Status | Meaning |
|--------|---------|
| `pending` | Default. Statement needs proof. |
| `validating` | Proof submitted or has issues being processed. |
| `true` | Verified. Can be cited as lemma. |
| `false` | Counterexample found. Cannot be proved. |
| `abandoned` | Beyond scope or no longer needed. |

For `validating` statements, check `validation.issues` vs `validation.responses` to determine sub-state.

## Task management
1. Object `problem`
- Tasks are managed via objects called "problem". A problem phrases a task to be resolved.
- Tasks are nested via the `preliminaries` property: if a problem is too complicated, agent-solve creates sub-problems. The sub-problem id is added to `preliminaries`.
- Progressive notes can be added to the `progresses` property.

2. Script `src/prob.py`
- Handles problem creation and update.

3. Script `src/prob_init.py`
- Handles initialization based on the original puzzle.

## Tree of logic
1. Object `statement`
- Logic trees are realized via objects called "statement". A statement is a vertex of the tree.
- Sub-statements are linked via the `preliminaries` property.

2. Script `src/state.py`
- Handles statement creation and update.

## Experience
- **To be developed**
- Similar to "memory" or "self-improving system".
- Supposed to enable the system to reflect on wrong answers and analyze what went wrong.
- Expected to inject past experiences when handling new puzzles.

## History
1. Script `src/utils.py`
- Has a LogManager that logs every change (creation or update) of objects.
- Each change is associated with a log id.

2. Script `src/rewind.py`
- Can rewind to any past status via log id.
- **Caution** This rewind process is non-reversible. Need to be careful to do so. Use github version control if you want to go back and force or even exploring multi-branches.
- A terminal confirmation is added to prevent agent mistakenly running this script.

## Developer's notes
- For demo:
    - Rely more on the model's capacity.
    - Missing a hook preventing write and edit during the process.
- For real development:
    - May change "problem" to "task".
    - May refine custom types to make more modular usage and skills.
    - May develop a status system to better control the workflow.
- For future development:
    - Experience system: the agent needs to learn during practice.
    - Object system: statements and problems naturally involve objects.
    - Terminology system: objects are defined regulated by terms, and experiences may be associated to terms as well.