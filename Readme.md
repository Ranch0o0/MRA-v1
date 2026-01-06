# Virtual environment
- **IMPORTANT** All scripts are run via virtual environment. The instructions to agents hard coded the virtual environment path which need to be replaced.
- One idea to do this is to wrap the python virtual environment by the alias `venv-python`, which is currently used in the instruction to all agents and skills.
```zsh
which venv-python
venv-python: aliased to /Users/zhenkun/Documents/Python/Virtual_environment/bin/python
```
- Or else one may need to modify the instruction to all agents and skills in `.claude/agents` and `.claude/skills`

# Quick start
1. To change puzzle: manually modify `puzzle.md`.

2. To start a new test: (make sure `puzzle.md` contains the puzzle you want to test)
- Use slash command `/start`

3. To resume solving the puzzle (interrupted for any reason or rewind to some status)
- Use slash command `/resume`

4. To run the puzzle-solving process for several steps ((changes in log id))
- Use slash command `/step $ARGUMENT`
- `$ARGUMENT` should be the number of steps you would like the claude code agent to proceed.

**Important** If any slash command does not work as expected, may check if global slash commands collide with project level slash command (actually I do not know if they might ever be a problem as claude code may have hieratical structure)

5. To rewind to a past status
- Find the log id you want to rewind to.
- Modify the main block of the script `src/rewind.py`
- Run the script, and confirm in terminal.

# System structure
This prototype has the following building blocks.

## Claude code system
1. Commands
Several commands has been included to quickly test on the puzzle.

2. Agents
Several agents have been designed to handle different type of logic tasks to solve the puzzle.

3. Skills
Several skills have been created to handle particular execution tasks involving scripts.

## Task management
1. Object `problem`
- Tasks are managed via objects called "problem". A problem phrases a task to be resolved.
- Tasks are nested via the `preliminaries` property.
- Progressive notes can be added to the `progresses` property.

2. Script `src/prob.py`
- Handles the problem creation and update.

3. Script `src/prob_init.py`
- Only handles the initialization from the original puzzle.

## Tree of logic
1. Object `statement`
- Logic tree are realized via objects called "statement". A statement is a vertex of the tree. Edges conceptually correspond to `hypothesis` property.

2. Script `src/state.py`
- Handles the statement creation and update.

## Experience
- To be developed.
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





