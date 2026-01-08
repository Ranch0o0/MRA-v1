# Goal
The goal of this project is to find a solution to the puzzle using the system already developed in this.

# Your role
You (claude code main agent) are the orchestrator of the whole system. Please monitor the progress of the system and call subagents when needed.

# Typical workflow
1. Understand the current status of the project (either by running the script `src/current.py` or via reports of subagents)

2. Determine the next object (problem or statement) to work on. 

3. Call relevant subagent to work on the object.

## Principle
- No background tasks. Simply wait for the subagents to finish their work before moving on to next step.
- As the orchestrator, do not work on actual problems or statements on your own.

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

## Claude code system
This is the native structure you (claude code agent) possess. In particular, the project utilizes the following:

1. Subagents
- `initializer`: this is the subagent specific on initializing the whole puzzle. Only trigger this agent once at the right start.
- `planer`: 

2. Skills

## Task management system
- 