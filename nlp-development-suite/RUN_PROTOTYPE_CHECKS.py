"""Run the dependency-free checks supported by the code-only prototype export."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parent


def run(label: str, command: list[str], env: dict[str, str]) -> None:
    print(f"[{label}] {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=ROOT, env=env, check=True)


def main() -> int:
    python = sys.executable
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = os.pathsep.join(
        str(ROOT / path)
        for path in (
            "projects/lexicon-core/src",
            "projects/natural-language-front-end",
            "projects/natural-language-front-end/tests",
            "development/nlp-offline-interpreter/src",
        )
    )
    run("prototype-boundary", [python, "-B", "VERIFY_PROTOTYPE_REPO.py"], env)
    run(
        "lexicon-core",
        [python, "-B", "-m", "unittest", "discover", "-s", "projects/lexicon-core/tests"],
        env,
    )
    run(
        "offline-interpreter",
        [python, "-B", "-m", "unittest", "discover", "-s", "development/nlp-offline-interpreter/tests"],
        env,
    )
    run(
        "grammar",
        [python, "-B", "-m", "unittest", "discover", "-s", "projects/natural-language-front-end/tests", "-p", "test_grammar_parser.py"],
        env,
    )
    run(
        "command-aliases",
        [python, "-B", "-m", "unittest", "discover", "-s", "projects/natural-language-front-end/tests", "-p", "test_command_aliases.py"],
        env,
    )
    data_free_omni_tests = [
        "test_omni_cli.OmniCliTests.test_complete_command_grammar",
        "test_omni_cli.OmniCliTests.test_unregistered_and_multiline_language_abstains",
        "test_omni_cli.OmniCliTests.test_read_list_and_search_within_root",
        "test_omni_cli.OmniCliTests.test_forged_intent_and_missing_root_rejected",
        "test_omni_cli.OmniCliTests.test_outside_path_and_symlink_are_rejected",
        "test_omni_cli.OmniCliTests.test_read_and_search_bounds",
        "test_omni_cli.OmniCliTests.test_command_line_exit_status",
    ]
    run("read-only-command-front-end", [python, "-B", "-m", "unittest", *data_free_omni_tests], env)
    node = shutil.which("node")
    js_files = sorted(
        path
        for base in (ROOT / "projects/lexicon-atlas", ROOT / "projects/file-atlas")
        for path in base.rglob("*")
        if path.is_file() and path.suffix.casefold() in {".js", ".mjs", ".cjs"}
    )
    if node:
        for path in js_files:
            run("javascript-syntax", [node, "--check", str(path)], env)
        javascript_status = "passed"
    else:
        javascript_status = "not_run_node_unavailable"
    print(json.dumps({
        "schema": "nlp-suite-prototype-checks/1",
        "status": "passed",
        "javascript_syntax": javascript_status,
        "data_profile": "code-only-no-dictionaries",
        "data_dependent_tests": "not_run",
        "publication_allowed": False,
        "deployment_allowed": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
