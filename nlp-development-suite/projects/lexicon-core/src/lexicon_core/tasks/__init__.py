"""Task-specific deterministic NLP modules."""

from .base import TaskModule, TaskProposal, TaskRequest, TaskResult
from .builtin import built_in_modules
from .router import ModuleMatch, RouteResult, route_request
from .dictionary import DictionaryModule
from .eliza_nxt import ElizaNxtModule
from .expert_control import ExpertControlModule
from .file_explorer import FileExplorerModule

__all__ = [
    "ModuleMatch", "RouteResult", "TaskModule", "TaskProposal", "TaskRequest", "TaskResult",
    "DictionaryModule", "ElizaNxtModule", "ExpertControlModule", "FileExplorerModule",
    "built_in_modules", "route_request",
]
