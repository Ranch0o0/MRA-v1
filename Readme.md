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
- Use slash command `/step $ARGUMENT`
- `$ARGUMENT` should be the number of steps you would like the claude code agent to proceed.
<exampe>
/step 5
</exampe>

**Important** If any slash command does not work as expected, may check if global slash commands collide with project level slash command (actually I do not know if they might ever be a problem as claude code may have hieratical structure)

5. To rewind to a past status
- Find the log id you want to rewind to.
- Modify the main block of the script `src/rewind.py`
- Run the script, and confirm in terminal.

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

2. Agents
Several agents have been designed to handle different type of logic tasks to solve the puzzle.
- `initializer`: to initialize the puzzle. Only called once at the start.
- `planer`:
- `prover`: 
- `checker`:

3. Skills
Several skills have been created to handle particular execution tasks involving scripts.

**Special remarks**
- The claude code system has a few building blocks: slash commands, subagents, skills, and many more (e.g. hooks, mcps). In this demo, we only use these three (as they are simple but already powerful).
- A simple principle: all three things are simply prompt/context engineering, and all three are about editing markdown files.
- Trade-off: all these three blocks are not hard-coded constraints for our math reasoning system. They are built upon the prompt-following capacity and large enough context window of the base model.

## Task management
1. Object `problem`
- Tasks are managed via objects called "problem". A problem phrases a task to be resolved.
- Tasks are nested via the `preliminaries` property: if the planer agent decide a problem is too complicated to be resolved directly, he will instead create sub-problems aiming partial progresses. The problem id will be added to preliminaries to indicate the nested relation.
- Progressive notes can be added to the `progresses` property.

2. Script `src/prob.py`
- Handles the problem creation and update.

3. Script `src/prob_init.py`
- Only handles the initialization based on the original puzzle.

## Tree of logic
1. Object `statement`
- Logic tree are realized via objects called "statement". A statement is a vertex of the tree. Edges conceptually correspond to `hypothesis` property.

2. Script `src/state.py`
- Handles the statement creation and update.

## Experience
- **To be developed**
- Similar to "memory" or "self-involving system".
- Supposed to make it possible for the system to reflect on wrong answers and analyze what has been done wrongly and what to be imporves.
- Expected to be able to inject past experiences when handling new puzzles.

## History
1. Script `src/utils.py`
- Has a log Manager that logs every changes (creation or update) of objects.
- Each change is associated with a log id.

2. Script `src/rewind.py`
- Can rewind to any past status via log id.
- **Caution** This rewind process is non-reversible. Need to be careful to do so.
- A terminal confirmation is added to prevent agent mistakenly running this script.





