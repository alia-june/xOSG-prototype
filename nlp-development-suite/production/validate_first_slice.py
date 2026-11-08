"""Smoke-test the proposed first release seam without executing operations."""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
CORE_SRC = ROOT / "projects" / "lexicon-core" / "src"
FRONTEND = ROOT / "projects" / "natural-language-front-end"
for path in (CORE_SRC, FRONTEND):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from lexicon_core import analyze_text  # noqa: E402
from lexicon_core.tasks import TaskRequest, built_in_modules, route_request  # noqa: E402
from omni_cli import parse_command  # noqa: E402


SOURCE = "find files named report in ."


def evaluate() -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    core_analysis = analyze_text("find files named report")
    routed = route_request(TaskRequest("find files named report"), built_in_modules())
    frontend_intent = parse_command(SOURCE, root=ROOT, use_wordnet=False)

    proposals = [proposal for result in routed.results for proposal in result.proposals]
    if core_analysis.intent.status != "proposal-only":
        errors.append("Lexicon Core intent did not remain proposal-only")
    if routed.status != "candidate-route":
        errors.append("Lexicon Core did not produce the expected candidate route")
    if not proposals:
        errors.append("Lexicon Core produced no task proposal")
    for proposal in proposals:
        if proposal.status != "proposal-only":
            errors.append("a task proposal did not remain proposal-only")
        if proposal.fields.get("execute") is not False:
            errors.append("a task proposal did not explicitly disable execution")
    if frontend_intent.status != "parsed":
        errors.append("front-end command was not parsed")
    if frontend_intent.capability != "find_files":
        errors.append("front-end capability was not find_files")
    if frontend_intent.arguments != {"name": "report", "path": "."}:
        errors.append("front-end arguments changed")
    if frontend_intent.as_dict().get("side_effect_class") != "read_only":
        errors.append("front-end side-effect class changed")

    frontend_sources = [
        path
        for path in FRONTEND.glob("*.py")
        if path.is_file() and path.name != Path(__file__).name
    ]
    direct_core_imports = [
        path.name
        for path in frontend_sources
        if "lexicon_core" in path.read_text(encoding="utf-8", errors="strict")
    ]
    integration_present = bool(direct_core_imports)
    successor_integration = (
        ROOT
        / "development"
        / "nlp-offline-interpreter"
        / "src"
        / "nlp_offline_interpreter"
        / "integration.py"
    ).is_file()
    report = {
        "schema": "nlp-first-slice-smoke/1",
        "status": "passed" if not errors else "failed",
        "release_proposal": "nlp-offline-interpreter/0.1",
        "operation_executed": False,
        "authority_effect": "NONE",
        "source": SOURCE,
        "core": {
            "intent": asdict(core_analysis.intent),
            "route_status": routed.status,
            "matches": [asdict(match) for match in routed.matches],
            "proposals": [asdict(proposal) for proposal in proposals],
        },
        "frontend": frontend_intent.as_dict(),
        "integration": {
            "direct_frontend_lexicon_core_imports": direct_core_imports,
            "present": integration_present,
            "successor_adapter_present": successor_integration,
            "finding": (
                "existing direct integration found"
                if integration_present
                else (
                    "successor adapter stages the explicit integration outside the immutable baseline"
                    if successor_integration
                    else "feasible independent outputs with an explicit integration gap"
                )
            ),
        },
        "errors": errors,
    }
    return report, errors


def main() -> int:
    try:
        report, errors = evaluate()
    except (ImportError, OSError, RuntimeError, UnicodeError, ValueError) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True, default=list))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
