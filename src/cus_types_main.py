from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class type_argument:
    cot: list[str]
    full: str

@dataclass
class type_trigger:
    phase: list[str]
    agents: list[str]
    situation: list[str]

@dataclass
class type_stats:
    count_usage: int = 0

@dataclass
class type_statement:
    id: str
    type: str
    hypothesis: list[str]
    conclusion: str

    # With default values:
    dependencies: list[str] = []
    status: str = "pending"
    reliability: float = 0.0
    stats: type_stats = type_stats()
    proof: type_argument = type_argument(cot=[], full="")

@dataclass
class type_experience:
    id: str
    content: str
    
    # With default values:
    explanation: str = ""
    trigger: type_trigger = type_trigger(phase=[], agents=[], situation=[])
    stats: type_stats = type_stats()

@dataclass
class type_problem:
    id: str
    hypothesis: list[str]
    objectives: list[str]
    
    # With default values:
    status: str = "unresolved"
    motivation: str = ""
    solution: type_argument = type_argument(cot=[], full="")
    