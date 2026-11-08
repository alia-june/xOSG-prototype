"""Run the P04 checks in a fresh offline environment and write an exact receipt."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parents[2]
P04 = Path(__file__).resolve().parent
REPORTS = (ROOT / "production" / "reports").resolve()
TAIL_LIMIT = 12_000


def tail(value: str) -> str:
    if len(value) <= TAIL_LIMIT:
        return value
    return f"[output truncated; original_chars={len(value)}]\n" + value[-TAIL_LIMIT:]


def run(label: str, command: list[str], cwd: Path, environment: dict[str, str], timeout: int) -> dict[str, object]:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=environment,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return {
            "id": label,
            "status": "passed" if completed.returncode == 0 else "failed",
            "returncode": completed.returncode,
            "duration_seconds": round(time.monotonic() - started, 3),
            "stdout": tail(completed.stdout),
            "stderr": tail(completed.stderr),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "id": label,
            "status": "timed_out",
            "duration_seconds": round(time.monotonic() - started, 3),
            "stdout": tail(exc.stdout or ""),
            "stderr": tail(exc.stderr or ""),
        }


def copy_successor(destination: Path) -> None:
    source = ROOT / "development" / "nlp-offline-interpreter"
    shutil.copytree(
        source,
        destination,
        ignore=shutil.ignore_patterns("dist", "build", "*.egg-info", "__pycache__", "*.pyc"),
    )


def report_path(value: Path) -> Path:
    resolved = value.resolve()
    if resolved.parent != REPORTS or resolved.suffix.lower() != ".json":
        raise ValueError(f"report must be a JSON file directly under {REPORTS}")
    if resolved.exists() or resolved.is_symlink():
        raise FileExistsError(f"refusing to replace report: {resolved}")
    return resolved


def git_source_state() -> dict[str, object]:
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if revision.returncode != 0 or status.returncode != 0:
        return {"kind": "unknown", "commit": None, "clean": False}
    return {
        "kind": "git",
        "commit": revision.stdout.strip(),
        "clean": not bool(status.stdout.strip()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    try:
        output = report_path(args.report)
    except (FileExistsError, ValueError) as exc:
        parser.error(str(exc))

    results: list[dict[str, object]] = []
    wheel_hashes: list[str] = []
    runtime_tag = f"py{sys.version_info.major}{sys.version_info.minor}"
    lock = P04 / f"requirements-{runtime_tag}.lock"
    if not lock.is_file():
        parser.error(f"unsupported runtime or missing lock: {runtime_tag}")
    environment = os.environ.copy()
    environment.update(
        {
            "PYTHONDONTWRITEBYTECODE": "1",
            "PIP_NO_INDEX": "1",
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
            "SOURCE_DATE_EPOCH": "1704067200",
        }
    )
    with tempfile.TemporaryDirectory(prefix="nlp-p04-stage-") as temporary:
        work = Path(temporary)
        venv = work / "venv"
        results.append(run("create-venv", [sys.executable, "-B", "-m", "venv", str(venv)], ROOT, environment, 120))
        python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        if results[-1]["status"] == "passed":
            results.append(
                run(
                    "offline-hash-install",
                    [
                        str(python),
                        "-B",
                        "-m",
                        "pip",
                        "install",
                        "--no-index",
                        "--find-links",
                        str(P04 / "wheelhouse"),
                        "--require-hashes",
                        "-r",
                        str(lock),
                    ],
                    ROOT,
                    environment,
                    180,
                )
            )
        if results[-1]["status"] == "passed":
            results.append(
                run(
                    "full-baseline",
                    [str(python), "-B", "production/run_checks.py", "--suite", "baseline"],
                    ROOT,
                    environment,
                    600,
                )
            )
        if results[-1]["status"] == "passed":
            for index in (1, 2):
                source = work / f"source-{index}"
                wheels = work / f"wheels-{index}"
                copy_successor(source)
                wheels.mkdir()
                result = run(
                    f"wheel-build-{index}",
                    [
                        str(python),
                        "-B",
                        "-m",
                        "pip",
                        "wheel",
                        "--no-deps",
                        "--no-index",
                        "--find-links",
                        str(P04 / "wheelhouse"),
                        "--use-pep517",
                        str(source),
                        "--wheel-dir",
                        str(wheels),
                    ],
                    ROOT,
                    environment,
                    180,
                )
                results.append(result)
                if result["status"] != "passed":
                    break
                built = list(wheels.glob("*.whl"))
                if len(built) != 1:
                    results.append({"id": f"wheel-count-{index}", "status": "failed"})
                    break
                wheel_hashes.append(sha256(built[0].read_bytes()).hexdigest())

    reproducible = len(wheel_hashes) == 2 and wheel_hashes[0] == wheel_hashes[1]
    if len(wheel_hashes) == 2:
        results.append(
            {
                "id": "wheel-reproducibility",
                "status": "passed" if reproducible else "failed",
                "sha256": wheel_hashes,
            }
        )
    passed = bool(results) and all(item.get("status") == "passed" for item in results) and reproducible
    source_state = git_source_state()
    if source_state["kind"] == "git" and source_state["clean"]:
        source_limit = f"Source tree was clean at Git commit {source_state['commit']}."
    elif source_state["kind"] == "git":
        source_limit = f"Source tree had uncommitted changes at Git commit {source_state['commit']}."
    else:
        source_limit = "Git source revision and cleanliness could not be established."
    runtime_limit = (
        f"Only CPython {sys.version_info.major}.{sys.version_info.minor} on "
        f"{platform.system()} {platform.machine()} was executed."
    )
    document = {
        "schema": "nlp-p04-clean-stage-report/1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if passed else "failed",
        "authority_effect": "P04_LOCAL_STAGING",
        "production_ready": False,
        "p04_phase_advanced": True,
        "network_install_allowed": False,
        "source_state": source_state,
        "runtime": sys.version,
        "runtime_tag": runtime_tag,
        "results": results,
        "limits": [
            "P03 and P04 are verified; this receipt is reproducibility evidence, not production readiness.",
            source_limit,
            runtime_limit,
        ],
    }
    with output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(document, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps({"report": str(output), "status": document["status"]}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
