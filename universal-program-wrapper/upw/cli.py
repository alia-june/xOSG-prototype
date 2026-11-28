from __future__ import annotations

import argparse
import json
import sys

from .core import UniversalProgramWrapper


def main() -> int:
    parser = argparse.ArgumentParser(description="Universal Program Wrapper reference CLI")
    parser.add_argument("--manifest", required=True, help="Path to a UPW manifest JSON file")
    args = parser.parse_args()

    try:
        request = json.load(sys.stdin)
        wrapper = UniversalProgramWrapper.from_file(args.manifest)
        response = wrapper.handle(request)
        json.dump(response, sys.stdout, separators=(",", ":"), ensure_ascii=False)
        sys.stdout.write("\n")
        return 0 if response["wrapper_outcome"] != "WRAPPER_ERROR" else 2
    except Exception as exc:
        # stdout remains machine JSON even for wrapper startup errors.
        response = {
            "protocol": "upw/0.1",
            "request_id": "",
            "wrapper_outcome": "WRAPPER_ERROR",
            "operation_id": None,
            "result": None,
            "raw": None,
            "diagnostics": [{"type": "startup", "message": f"{type(exc).__name__}: {exc}"}],
            "evidence": [],
        }
        json.dump(response, sys.stdout, separators=(",", ":"), ensure_ascii=False)
        sys.stdout.write("\n")
        print(f"UPW startup error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
