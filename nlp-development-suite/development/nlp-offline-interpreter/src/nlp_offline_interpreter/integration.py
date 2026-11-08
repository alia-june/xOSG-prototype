"""Generic offline interpretation API and plan-only command-line interface.

This module adapts the existing deterministic front end and Lexicon Core task
modules to the generic ``lexicon_core.interpretation`` contract.  It exposes no
operation execution function.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import lru_cache
from importlib import import_module, util
from itertools import islice
import json
import os
from pathlib import Path
import sys
from typing import Any, Iterable, TYPE_CHECKING

from .core import (
    InterpretationCandidate,
    InterpretationRequest,
    Interpreter,
    LayerResult,
    UnresolvedRegion,
    canonical_json,
)
from .basic import analyze_text
if TYPE_CHECKING:
    from lexicon_core.tasks import TaskModule
else:
    TaskModule = Any


PUBLIC_API_VERSION = "nlp-offline-interpreter/0.1"
MAX_TASK_MODULES = 256
REQUIRED_INTEGRATION_MODULES = (
    "lexicon_core.tasks",
    "omni_cli",
    "wordnet_lexicon",
)


class IntegrationUnavailableError(RuntimeError):
    """The optional historical-suite adapters are not installed or visible."""


def integration_status() -> dict[str, object]:
    """Report optional adapter availability without importing suite modules."""

    missing: list[str] = []
    for name in REQUIRED_INTEGRATION_MODULES:
        try:
            available = util.find_spec(name) is not None
        except (ImportError, ModuleNotFoundError, AttributeError, ValueError):
            available = False
        if not available:
            missing.append(name)
    return {
        "schema": "nlp-offline-integration-status/1",
        "available": not missing,
        "required_modules": list(REQUIRED_INTEGRATION_MODULES),
        "missing_modules": missing,
        "authority_effect": "NONE",
        "execution_allowed": False,
    }


@dataclass(frozen=True)
class _SuiteDependencies:
    task_request: Any
    built_in_modules: Any
    route_request: Any
    parse_command: Any
    omni_version: str
    default_data_dir: Path


@lru_cache(maxsize=1)
def _load_suite_dependencies() -> _SuiteDependencies:
    status = integration_status()
    if not status["available"]:
        missing = ", ".join(status["missing_modules"])
        raise IntegrationUnavailableError(
            f"optional suite integration is unavailable; missing modules: {missing}"
        )
    try:
        tasks = import_module("lexicon_core.tasks")
        omni = import_module("omni_cli")
        wordnet = import_module("wordnet_lexicon")
    except (ImportError, AttributeError) as exc:
        raise IntegrationUnavailableError(
            f"optional suite integration could not be loaded: {type(exc).__name__}"
        ) from exc
    return _SuiteDependencies(
        task_request=tasks.TaskRequest,
        built_in_modules=tasks.built_in_modules,
        route_request=tasks.route_request,
        parse_command=omni.parse_command,
        omni_version=omni.VERSION,
        default_data_dir=Path(wordnet.DEFAULT_DATA_DIR),
    )


class OmniProposalLayer:
    """Adapt deterministic aliases and local lexical candidates without execution."""

    layer_id = "omni-front-end"
    layer_version = "unavailable"

    def __init__(self, *, use_wordnet: bool = True, wordnet_dir: Path | None = None) -> None:
        if not isinstance(use_wordnet, bool):
            raise TypeError("use_wordnet must be a Boolean")
        if wordnet_dir is not None and not isinstance(wordnet_dir, (str, os.PathLike)):
            raise TypeError("wordnet_dir must be a filesystem path")
        dependencies = _load_suite_dependencies()
        self.layer_version = dependencies.omni_version
        self._parse_command = dependencies.parse_command
        self.use_wordnet = use_wordnet
        self.wordnet_dir = Path(
            dependencies.default_data_dir if wordnet_dir is None else wordnet_dir
        )

    def interpret(self, request: InterpretationRequest) -> LayerResult:
        intent = self._parse_command(
            request.source_text,
            root=None,
            use_wordnet=self.use_wordnet,
            wordnet_dir=self.wordnet_dir,
            web_provider=None,
            llm_provider=None,
        )
        provenance = (
            "deterministic_alias"
            if intent.status in {"parsed", "collision"}
            else "lexical_or_local_history_candidate"
        )
        candidates = tuple(
            InterpretationCandidate(
                candidate_id=f"{self.layer_id}:{candidate.rule_id}:{rank}",
                operation=candidate.capability,
                arguments=dict(candidate.arguments),
                layer_id=self.layer_id,
                provenance_class=provenance,
                evidence=tuple(candidate.evidence),
                confidence={
                    "value": candidate.score,
                    "semantics": "layer-local ranking only; not probability or authority",
                },
            )
            for rank, candidate in enumerate(intent.candidates, 1)
        )
        unresolved = ()
        if not candidates:
            unresolved = (
                UnresolvedRegion(
                    0,
                    len(request.source_text),
                    intent.reason or "front end produced no candidate",
                    self.layer_id,
                ),
            )
        if len(candidates) > 1:
            status = "collision"
        elif candidates:
            status = "candidates"
        else:
            status = "no_match"
        diagnostics = tuple(
            f"{item.get('layer', 'unknown')}:{item.get('status', 'unknown')}"
            for item in intent.layer_trace
        )
        return LayerResult(
            self.layer_id,
            self.layer_version,
            status,
            candidates,
            unresolved,
            diagnostics,
        )


class LexiconCoreTaskLayer:
    """Adapt any supplied Lexicon Core task modules as proposal-only fallbacks."""

    layer_id = "lexicon-core-tasks"
    layer_version = "lexicon-core-tasks/0.1"

    def __init__(self, modules: Iterable[TaskModule] | None = None) -> None:
        dependencies = _load_suite_dependencies()
        self._task_request = dependencies.task_request
        self._route_request = dependencies.route_request
        source = dependencies.built_in_modules() if modules is None else modules
        self.modules = tuple(islice(source, MAX_TASK_MODULES + 1))
        if len(self.modules) > MAX_TASK_MODULES:
            raise ValueError("task module count exceeds the bound")

    def interpret(self, request: InterpretationRequest) -> LayerResult:
        routed = self._route_request(
            self._task_request(request.source_text, metadata=request.metadata),
            self.modules,
        )
        candidates: list[InterpretationCandidate] = []
        index = 0
        for result in routed.results:
            for proposal in result.proposals:
                index += 1
                candidates.append(
                    InterpretationCandidate(
                        candidate_id=(
                            f"{self.layer_id}:{proposal.module_id}:{proposal.operation}:{index}"
                        ),
                        operation=f"{proposal.module_id}.{proposal.operation}",
                        arguments=dict(proposal.fields),
                        layer_id=self.layer_id,
                        provenance_class="deterministic_task_rule",
                        evidence=tuple(proposal.evidence),
                        confidence={
                            "route_status": routed.status,
                            "semantics": "module routing evidence; not authority",
                        },
                    )
                )
        unresolved = ()
        if not candidates:
            unresolved = (
                UnresolvedRegion(
                    0,
                    len(request.source_text),
                    "no task module met the routing threshold",
                    self.layer_id,
                ),
            )
        status = "collision" if len(candidates) > 1 else "candidates" if candidates else "no_match"
        diagnostics = (f"route_status:{routed.status}",)
        return LayerResult(
            self.layer_id,
            self.layer_version,
            status,
            tuple(candidates),
            unresolved,
            diagnostics,
        )


def build_interpreter(
    *,
    use_wordnet: bool = True,
    wordnet_dir: Path | None = None,
    modules: Iterable[TaskModule] | None = None,
    mode: str = "first_candidate",
) -> Interpreter:
    """Build the default offline interpreter from replaceable ordered layers."""

    return Interpreter(
        (
            OmniProposalLayer(use_wordnet=use_wordnet, wordnet_dir=wordnet_dir),
            LexiconCoreTaskLayer(modules),
        ),
        mode=mode,
        max_source_chars=1024,
    )


def interpret_text(
    source_text: str,
    *,
    use_wordnet: bool = True,
    wordnet_dir: Path | None = None,
    modules: Iterable[TaskModule] | None = None,
    mode: str = "first_candidate",
):
    """Return a generic non-executing interpretation result."""

    interpreter = build_interpreter(
        use_wordnet=use_wordnet,
        wordnet_dir=wordnet_dir,
        modules=modules,
        mode=mode,
    )
    return interpreter.interpret(
        source_text,
        metadata={"public_api_version": PUBLIC_API_VERSION},
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", nargs="*", help="Natural-language request to interpret")
    parser.add_argument(
        "--check-integration",
        action="store_true",
        help="Report optional suite-adapter availability without interpreting text",
    )
    parser.add_argument(
        "--basic",
        action="store_true",
        help="Run dependency-free bounded surface analysis without suite adapters",
    )
    parser.add_argument("--no-wordnet", action="store_true", help="Disable local OEWN evidence")
    parser.add_argument(
        "--wordnet-dir",
        type=Path,
        default=None,
        help="Path to the pinned local WordNet database",
    )
    parser.add_argument(
        "--collect-all",
        action="store_true",
        help="Collect every layer instead of stopping at the first layer with candidates",
    )
    args = parser.parse_args(argv)
    if args.check_integration:
        status = integration_status()
        print(json.dumps(status, sort_keys=True))
        return 0 if status["available"] else 4
    if not args.request:
        parser.error("a request is required unless --check-integration is used")
    if args.basic:
        result = analyze_text(" ".join(args.request))
        print(canonical_json(result))
        return 0 if result.status in {"parsed_single", "partial"} else 2
    try:
        result = interpret_text(
            " ".join(args.request),
            use_wordnet=not args.no_wordnet,
            wordnet_dir=args.wordnet_dir,
            mode="collect_all" if args.collect_all else "first_candidate",
        )
    except IntegrationUnavailableError as exc:
        print(
            json.dumps(
                {
                    "schema": "nlp-offline-integration-error/1",
                    "status": "unavailable",
                    "reason": str(exc),
                    "authority_effect": "NONE",
                    "execution_allowed": False,
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 4
    print(canonical_json(result))
    if result.status in {"invalid_input", "unparsed"}:
        return 2
    if result.status == "collision":
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
