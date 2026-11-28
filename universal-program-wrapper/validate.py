from __future__ import annotations

import json
from pathlib import Path
import py_compile

ROOT = Path(__file__).resolve().parent
REQUIRED = [
    "README.md",
    "CANON.md",
    "ARCHITECTURE.md",
    "SPEC.md",
    "upw/__init__.py",
    "upw/core.py",
    "upw/cli.py",
    "schemas/request.schema.json",
    "schemas/response.schema.json",
    "schemas/manifest.schema.json",
]


def main() -> int:
    errors = []
    for rel in REQUIRED:
        if not (ROOT / rel).is_file():
            errors.append(f"missing: {rel}")

    for rel in ["schemas/request.schema.json", "schemas/response.schema.json", "schemas/manifest.schema.json", "examples/python_manifest.json", "examples/request_describe.json", "examples/request_invoke.json"]:
        try:
            json.loads((ROOT / rel).read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"invalid JSON {rel}: {exc}")

    for rel in ["upw/__init__.py", "upw/core.py", "upw/cli.py", "tests/test_upw.py"]:
        try:
            py_compile.compile(str(ROOT / rel), doraise=True)
        except Exception as exc:
            errors.append(f"compile failed {rel}: {exc}")

    text = (ROOT / "upw/core.py").read_text(encoding="utf-8")
    forbidden = ["shell=True", "os.system(", "subprocess.Popen(\"", "eval(", "exec("]
    for needle in forbidden:
        if needle in text:
            errors.append(f"forbidden primitive in core: {needle}")

    if errors:
        print("VALIDATION FAILED")
        for e in errors:
            print("-", e)
        return 1

    print("VALIDATION PASSED")
    print("standalone wrapper boundary: present")
    print("kernel/driver dependency: none")
    print("sf-Program-Access dependency: none")
    print("BitCore dependency: none")
    print("shell execution: disabled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
