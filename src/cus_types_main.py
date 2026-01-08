from dataclasses import dataclass, field
from typing import Optional, Any, Union

@dataclass
class type_argument:
    cot: list[str] = field(default_factory=list)
    full: str = ""
    ref: list[str] = field(default_factory=list)  # renamed from 'reference'

@dataclass
class type_validation:
    issues: list[str] = field(default_factory=list)
    responses: list[str] = field(default_factory=list)

@dataclass
class type_trigger:
    phase: list[str] = field(default_factory=list)
    agents: list[str] = field(default_factory=list)
    situation: list[str] = field(default_factory=list)

@dataclass
class type_stats:
    count_usage: int = 0

@dataclass
class type_statement:
    id: str
    type: str
    conclusion: list[str]

    # With default values:
    hypothesis: list[str] = field(default_factory=list)
    preliminaries: list[str] = field(default_factory=list)
    status: str = "pending"
    reliability: float = 0.0
    stats: type_stats = field(default_factory=type_stats)
    proof: type_argument = field(default_factory=type_argument)
    validation: type_validation = field(default_factory=type_validation)

@dataclass
class type_experience:
    id: str
    content: str

    # With default values:
    explanation: str = ""
    trigger: type_trigger = field(default_factory=type_trigger)
    stats: type_stats = field(default_factory=type_stats)

@dataclass
class type_problem:
    id: str
    hypothesis: list[str]
    objectives: list[str]

    # With default values:
    status: str = "unresolved"
    priority: str = ""
    summary: str =""
    progresses: list[str] = field(default_factory=list)
    preliminaries: list[str] = field(default_factory=list)
    solution: type_argument = field(default_factory=type_argument)


@dataclass
class type_object_change:
    """Represents a change operation (create or update) for an object."""
    change_type: str  # "create" or "update"
    obj: Union[type_problem, type_statement]  # the object to be changed
    updates: Optional[dict] = None  # for update operations, the updates dict
