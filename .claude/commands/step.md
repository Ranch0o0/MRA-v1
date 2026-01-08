---
description: Start or resume to solve the puzzle.
argument-hint: [number of steps to run]
---

Please start or resume the project to solve the puzzle and run it in $ARGUMENTS steps.

Please:
- run script `src/current.py` to read the current log id in the form `l-{{current_index}}`.
- determine the {{terminate_index}} by adding the number of steps ($ARGUMENTS) to {{current_index}}, and thus determine when to stop the project.
- Each time receiving the task completion report from a subagent, run `src/current.py` again to examine the new log id, and decide if to continue or stop.

**Important**
If $ARGUMENTS does not contain information for how many steps to run, please run 3 steps by default.