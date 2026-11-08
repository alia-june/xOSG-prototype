"""Built-in task module collection."""

from __future__ import annotations

from .dictionary import DictionaryModule
from .eliza_nxt import ElizaNxtModule
from .expert_control import ExpertControlModule
from .file_explorer import FileExplorerModule


def built_in_modules():
    return (DictionaryModule(), FileExplorerModule(), ExpertControlModule(), ElizaNxtModule())
