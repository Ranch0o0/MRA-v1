---
description: Start or resume to solve the puzzle.
argument-hint: [number of steps to run]
---

Please start or resume to solve the puzzle by ONE step, with the following human instruction:
$ARGUMENTS

Note: if custom argument is missing, report error back to user. 

Please:
- Parse two infor: which agent to run next, and what are the human instructions to be passed to the subagent. 
- Run script `src/current.py` to read the current log id.
- Call targeted subagent and pass the human instructions to move one step ahead. 
- Run script `src/current.py` after receiving the subagent report. If the log id has changed (+1) then stop and report to the user.