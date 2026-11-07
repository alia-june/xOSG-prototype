"""Shared immutable declarative contract preflight, not a microserver itself."""
from pathlib import Path
import json
from jsonschema import Draft202012Validator
from .protocol import MAX_FAULTS

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "contracts" / "manifest_v0_2.schema.json"


def schema_faults(manifest):
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(manifest),
                    key=lambda e: (tuple(str(x) for x in e.absolute_path), e.message))
    return [{"code": "SCHEMA_VIOLATION", "detail": e.message[:800]} for e in errors[:MAX_FAULTS]]
