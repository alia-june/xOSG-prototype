"""Bounded, deterministic JSON CLI protocol. No execution/admission authority."""
import hashlib
import json
import math
import sys
from typing import Any

PROTOCOL_VERSION = "0.3.0"
MAX_INPUT_BYTES = 2 * 1024 * 1024
MAX_RESPONSE_BYTES = 4 * 1024 * 1024
MAX_FAULTS = 20
VALID_OPERATION = {
    "schema-gate": "validate_manifest_schema",
    "graph-gate": "validate_manifest_graph",
}


class ContractRefusal(Exception):
    def __init__(self, code: str, detail: str):
        super().__init__(detail)
        self.code = code
        self.detail = detail


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ContractRefusal("DUPLICATE_JSON_KEY", "repeated member name in JSON")
        result[key] = value
    return result


def _reject_constant(value):
    raise ContractRefusal("NON_STANDARD_JSON_NUMBER", "NaN or infinity is forbidden")


def forbid_null(obj: Any):
    stack = [obj]
    while stack:
        node = stack.pop()
        if node is None:
            raise ContractRefusal("NULL_FORBIDDEN", "use a typed named sentinel, not null")
        if isinstance(node, float) and not math.isfinite(node):
            raise ContractRefusal("NON_FINITE_NUMBER", "non-finite JSON numeric value is forbidden")
        if isinstance(node, dict):
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)


def strict_json(raw: bytes):
    if not raw or len(raw) > MAX_INPUT_BYTES:
        raise ContractRefusal("SIZE_OR_EMPTY", "input must be one bounded JSON value")
    try:
        obj = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_pairs,
                         parse_constant=_reject_constant)
    except UnicodeDecodeError:
        raise ContractRefusal("BAD_ENCODING", "input must be UTF-8") from None
    except (json.JSONDecodeError, RecursionError, ValueError):
        raise ContractRefusal("MALFORMED_JSON", "cannot parse bounded JSON value") from None
    forbid_null(obj)
    return obj


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(obj: Any) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def validate_envelope(obj: Any, service: str):
    if not isinstance(obj, dict) or set(obj) != {"protocol_version", "request_id", "operation", "authority", "payload"}:
        raise ContractRefusal("ENVELOPE_SHAPE", "invalid or extra request envelope fields")
    if obj["protocol_version"] != PROTOCOL_VERSION:
        raise ContractRefusal("PROTOCOL_VERSION", "incompatible protocol version")
    if not isinstance(obj["request_id"], str) or not 1 <= len(obj["request_id"]) <= 180:
        raise ContractRefusal("REQUEST_ID", "request_id must be a bounded non-empty string")
    if obj["operation"] != VALID_OPERATION[service]:
        raise ContractRefusal("OPERATION", "operation not offered by this microserver")
    if obj["authority"] != {"mode": "READ_ONLY_CANDIDATE", "basis": "EXPLICIT_LOCAL_INVOKER"}:
        raise ContractRefusal("AUTHORITY_SCOPE", "only local read-only candidate evaluation offered")
    if not isinstance(obj["payload"], dict) or set(obj["payload"]) != {"manifest"}:
        raise ContractRefusal("PAYLOAD_SHAPE", "payload must contain only manifest")
    if not isinstance(obj["payload"]["manifest"], dict):
        raise ContractRefusal("MANIFEST_SHAPE", "manifest must be a JSON object")
    return obj["payload"]["manifest"]


def response(service: str, request_id: str, decision: str, data: Any, faults: list, input_sha256: str):
    return {
        "protocol_version": PROTOCOL_VERSION,
        "request_id": request_id,
        "service_id": service,
        "operation": VALID_OPERATION[service],
        "decision": decision,
        "disposition": "CANDIDATE_ONLY",
        "admission": "NOT_ADMITTED",
        "input_sha256": input_sha256,
        "data": data,
        "faults": faults[:MAX_FAULTS],
    }


def refusal(service: str, request_id: str, code: str, detail: str):
    return response(service, request_id, "REFUSED", {"kind": "sentinel", "code": "SENTINEL_ABSENT"},
                    [{"code": code, "detail": detail[:800]}], "SENTINEL_UNRESOLVED")


def emit_json(obj):
    forbid_null(obj)
    output = canonical_bytes(obj) + b"\n"
    if len(output) > MAX_RESPONSE_BYTES:
        raise RuntimeError("response exceeds local output bound")
    sys.stdout.buffer.write(output)
    sys.stdout.buffer.flush()


def read_one_request():
    raw = sys.stdin.buffer.readline(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise ContractRefusal("SIZE_OR_EMPTY", "request exceeds 2 MiB maximum")
    if sys.stdin.buffer.read(1):
        raise ContractRefusal("MULTIPLE_MESSAGES", "exactly one JSON request is permitted")
    return strict_json(raw)


def serve(service: str, validator):
    request_id = "SENTINEL_UNRESOLVED"
    try:
        req = read_one_request()
        if isinstance(req, dict) and isinstance(req.get("request_id"), str) and 1 <= len(req["request_id"]) <= 180:
            request_id = req["request_id"]
        manifest = validate_envelope(req, service)
        result = validator(manifest)
        emit_json(response(service, request_id, "ACCEPTED" if not result["faults"] else "REFUSED",
                           result["data"] if not result["faults"] else {"kind": "sentinel", "code": "SENTINEL_ABSENT"},
                           result["faults"], result["input_sha256"]))
    except ContractRefusal as ex:
        emit_json(refusal(service, request_id, ex.code, ex.detail))
    except Exception as ex:
        # Do not disclose untrusted runtime paths or traceback in protocol output.
        emit_json(refusal(service, request_id, "INTERNAL_FAILURE", "service failed closed"))
