"""Identity-only composition glue. Spawn separate candidate JSON CLI processes.

This module is NOT an admission controller, authorization server, hardened Crete
join, transport authentication layer, or security sandbox.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from .protocol import (ContractRefusal, MAX_INPUT_BYTES, PROTOCOL_VERSION,
                       canonical_bytes, digest, forbid_null, strict_json)

ROOT = Path(__file__).resolve().parent.parent


def invoke(service, manifest, request_id, timeout=5):
    request = {
        "protocol_version": PROTOCOL_VERSION,
        "request_id": request_id,
        "operation": {"schema-gate": "validate_manifest_schema", "graph-gate": "validate_manifest_graph"}[service],
        "authority": {"mode": "READ_ONLY_CANDIDATE", "basis": "EXPLICIT_LOCAL_INVOKER"},
        "payload": {"manifest": manifest},
    }
    data = canonical_bytes(request) + b"\n"
    if len(data) > MAX_INPUT_BYTES:
        raise ContractRefusal("REQUEST_TOO_LARGE", "message exceeds local input ceiling")
    module = {"schema-gate": "microtrans.schema_gate", "graph-gate": "microtrans.graph_gate"}[service]
    try:
        p = subprocess.run([sys.executable, "-m", module], input=data, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, cwd=ROOT, timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        raise ContractRefusal("SERVICE_TIMEOUT", service + " did not respond within bound") from None
    if p.returncode != 0 or len(p.stdout) > 4 * 1024 * 1024:
        raise ContractRefusal("SERVICE_FAILURE", service + " failed or exceeded response ceiling")
    try:
        out = strict_json(p.stdout)
    except ContractRefusal:
        raise ContractRefusal("BAD_SERVICE_RESPONSE", "service response was not valid bounded JSON") from None
    expected = {"protocol_version", "request_id", "service_id", "operation", "decision", "disposition", "admission", "input_sha256", "data", "faults"}
    if not isinstance(out, dict) or set(out) != expected:
        raise ContractRefusal("BAD_SERVICE_RESPONSE", "unexpected response members")
    for k, v in {"protocol_version": PROTOCOL_VERSION, "request_id": request_id,
                 "service_id": service, "operation": request["operation"],
                 "disposition": "CANDIDATE_ONLY", "admission": "NOT_ADMITTED"}.items():
        if out[k] != v:
            raise ContractRefusal("BAD_SERVICE_RESPONSE", "response identity or disposition mismatch")
    if out["decision"] not in ("ACCEPTED", "REFUSED") or not isinstance(out["faults"], list):
        raise ContractRefusal("BAD_SERVICE_RESPONSE", "invalid decision or faults")
    if (out["decision"] == "ACCEPTED" and out["faults"]) or (out["decision"] == "REFUSED" and not out["faults"]):
        raise ContractRefusal("BAD_SERVICE_RESPONSE", "decision and fault state disagree")
    if not isinstance(out["input_sha256"], str):
        raise ContractRefusal("BAD_SERVICE_RESPONSE", "missing input digest declaration")
    return out


def compose(manifest, request_id="local-compose-001", runner=invoke):
    """Return one structured candidate-only receipt. Never publish/admit/execute target APIs."""
    transcript = []
    try:
        forbid_null(manifest)
        stage_a = runner("schema-gate", manifest, request_id + ":schema")
        transcript.append({"service": "schema-gate", "decision": stage_a["decision"], "faults": stage_a["faults"]})
        if stage_a["decision"] != "ACCEPTED":
            raise ContractRefusal("SCHEMA_REFUSED", "upstream refusal; graph gate not invoked")
        if not isinstance(stage_a["data"], dict):
            raise ContractRefusal("GLUE_DATA_SHAPE", "unexpected upstream output")
        forwarded = stage_a["data"]
        if forwarded != manifest or stage_a["input_sha256"] != digest(forwarded):
            raise ContractRefusal("GLUE_INTEGRITY", "identity-only edge changed its payload")
        stage_b = runner("graph-gate", forwarded, request_id + ":graph")
        transcript.append({"service": "graph-gate", "decision": stage_b["decision"], "faults": stage_b["faults"]})
        if stage_b["decision"] != "ACCEPTED":
            raise ContractRefusal("GRAPH_REFUSED", "downstream refusal; composition not accepted")
        if not isinstance(stage_b["data"], dict) or stage_b["input_sha256"] != digest(forwarded) or stage_b["data"].get("manifest_sha256") != digest(forwarded) or stage_b["data"].get("graph_check") != "STATIC_PASSED_NOT_ADMITTED":
            raise ContractRefusal("GLUE_INTEGRITY", "downstream digest/status mismatch")
        return {"protocol_version": PROTOCOL_VERSION, "request_id": request_id,
                "composition": "schema-gate -> ordinary-glue -> graph-gate",
                "decision": "STATIC_PASSED", "disposition": "CANDIDATE_ONLY",
                "admission": "NOT_ADMITTED", "publication": "NOT_PUBLISHED",
                "manifest_sha256": digest(manifest), "transcript": transcript,
                "faults": []}
    except ContractRefusal as ex:
        return {"protocol_version": PROTOCOL_VERSION, "request_id": request_id,
                "composition": "schema-gate -> ordinary-glue -> graph-gate",
                "decision": "REFUSED", "disposition": "CANDIDATE_ONLY",
                "admission": "NOT_ADMITTED", "publication": "NOT_PUBLISHED",
                "manifest_sha256": digest(manifest) if isinstance(manifest, dict) else "SENTINEL_UNRESOLVED",
                "transcript": transcript, "faults": [{"code": ex.code, "detail": ex.detail}]}


def main():
    parser = argparse.ArgumentParser(description="Static candidate-only microserver composition")
    parser.add_argument("manifest", help="JSON manifest path; read only")
    parser.add_argument("--request-id", default="local-compose-001")
    args = parser.parse_args()
    try:
        raw = Path(args.manifest).read_bytes()
        manifest = strict_json(raw)
        if not isinstance(manifest, dict):
            raise ContractRefusal("MANIFEST_SHAPE", "manifest must be object")
        receipt = compose(manifest, request_id=args.request_id)
    except (ContractRefusal, OSError) as ex:
        code = ex.code if isinstance(ex, ContractRefusal) else "SOURCE_READ_REFUSED"
        receipt = {"protocol_version": PROTOCOL_VERSION,
                   "request_id": args.request_id, "composition": "schema-gate -> ordinary-glue -> graph-gate",
                   "decision": "REFUSED", "disposition": "CANDIDATE_ONLY",
                   "admission": "NOT_ADMITTED", "publication": "NOT_PUBLISHED",
                   "manifest_sha256": "SENTINEL_UNRESOLVED", "transcript": [],
                   "faults": [{"code": code, "detail": "candidate input was rejected"}]}
    sys.stdout.buffer.write(canonical_bytes(receipt) + b"\n")
    return 0 if receipt["decision"] == "STATIC_PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
