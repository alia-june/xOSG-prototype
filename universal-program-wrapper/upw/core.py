from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Mapping, Optional
import json
import os
import subprocess

PROTOCOL = "upw/0.1"
CONTROL_KINDS = {"describe", "operations", "schema", "version", "status", "invoke"}
EVIDENCE_LEVELS = {"declared", "discovered", "tested", "observed", "attested"}
OUTCOMES = {"SUCCESS", "NO_CHANGE", "PARTIAL", "FAILED", "ABORTED", "UNKNOWN", "WRAPPER_ERROR"}


class WrapperError(Exception):
    pass


@dataclass(frozen=True)
class RawResult:
    exit_code: int
    stdout: str
    stderr: str

    def as_dict(self) -> Dict[str, Any]:
        return {"exit_code": self.exit_code, "stdout": self.stdout, "stderr": self.stderr}


NativeHandler = Callable[[Mapping[str, Any], Mapping[str, Any]], Dict[str, Any]]


class UniversalProgramWrapper:
    def __init__(self, manifest: Mapping[str, Any]):
        self.manifest = dict(manifest)
        self._native_handlers: Dict[str, NativeHandler] = {}
        self._validate_manifest()
        self.operations = {op["operation_id"]: dict(op) for op in self.manifest["operations"]}

    @classmethod
    def from_file(cls, path: str) -> "UniversalProgramWrapper":
        with open(path, "r", encoding="utf-8") as fh:
            return cls(json.load(fh))

    def register_native(self, operation_id: str, handler: NativeHandler) -> None:
        op = self.operations.get(operation_id)
        if not op:
            raise WrapperError(f"unknown operation_id: {operation_id}")
        if op.get("adapter", {}).get("type") != "native":
            raise WrapperError(f"operation {operation_id} is not declared native")
        self._native_handlers[operation_id] = handler

    def handle(self, request: Mapping[str, Any]) -> Dict[str, Any]:
        request_id = str(request.get("request_id", ""))
        try:
            self._validate_request(request)
            kind = request["kind"]
            if kind == "describe":
                return self._ok(request_id, result=self._describe())
            if kind == "operations":
                return self._ok(request_id, result=[self._public_operation(op) for op in self.operations.values()])
            if kind == "schema":
                return self._ok(request_id, result={"request": "schemas/request.schema.json", "response": "schemas/response.schema.json", "manifest": "schemas/manifest.schema.json"})
            if kind == "version":
                return self._ok(request_id, result={"protocol": PROTOCOL, "manifest_version": self.manifest["manifest_version"]})
            if kind == "status":
                return self._ok(request_id, result={"ready": True, "operation_count": len(self.operations)})
            return self._invoke(request)
        except WrapperError as exc:
            return self._response(request_id, "WRAPPER_ERROR", diagnostics=[{"type": "wrapper", "message": str(exc)}])
        except Exception as exc:  # boundary containment; details stay diagnostic
            return self._response(request_id, "WRAPPER_ERROR", diagnostics=[{"type": "internal", "message": f"{type(exc).__name__}: {exc}"}])

    def _validate_manifest(self) -> None:
        if self.manifest.get("manifest_version") != "upw-manifest/0.1":
            raise WrapperError("unsupported manifest_version")
        program = self.manifest.get("program")
        if not isinstance(program, dict) or not program.get("program_id"):
            raise WrapperError("manifest.program.program_id is required")
        operations = self.manifest.get("operations")
        if not isinstance(operations, list):
            raise WrapperError("manifest.operations must be an array")
        seen = set()
        for op in operations:
            if not isinstance(op, dict) or not op.get("operation_id"):
                raise WrapperError("every operation requires operation_id")
            oid = op["operation_id"]
            if oid in seen:
                raise WrapperError(f"duplicate operation_id: {oid}")
            seen.add(oid)
            evidence = op.get("evidence_level", "declared")
            if evidence not in EVIDENCE_LEVELS:
                raise WrapperError(f"invalid evidence_level for {oid}")
            adapter = op.get("adapter")
            if not isinstance(adapter, dict) or adapter.get("type") not in {"legacy_cli", "native"}:
                raise WrapperError(f"unsupported adapter for {oid}")
            if adapter.get("type") == "legacy_cli":
                exe = adapter.get("executable")
                if not isinstance(exe, str) or not os.path.isabs(exe):
                    raise WrapperError(f"legacy_cli operation {oid} requires an exact absolute executable path")

    def _validate_request(self, request: Mapping[str, Any]) -> None:
        if request.get("protocol") != PROTOCOL:
            raise WrapperError("unsupported protocol")
        if not isinstance(request.get("request_id"), str) or not request["request_id"]:
            raise WrapperError("request_id is required")
        kind = request.get("kind")
        if kind not in CONTROL_KINDS:
            raise WrapperError("unknown request kind")
        if kind == "invoke":
            oid = request.get("operation_id")
            if not isinstance(oid, str) or oid not in self.operations:
                raise WrapperError("unknown or missing operation_id")
            if not isinstance(request.get("input"), dict):
                raise WrapperError("invoke input must be an object")
            self._validate_input(self.operations[oid], request["input"])
        for field in ("provenance", "authority_context", "options"):
            if field in request and not isinstance(request[field], dict):
                raise WrapperError(f"{field} must be an object")

    def _validate_input(self, op: Mapping[str, Any], data: Mapping[str, Any]) -> None:
        spec = op.get("input", {})
        if not isinstance(spec, dict):
            raise WrapperError("operation input spec must be an object")
        fields = spec.get("fields", {})
        allow_extra = bool(spec.get("allow_extra", False))
        if not isinstance(fields, dict):
            raise WrapperError("input.fields must be an object")
        for name, fspec in fields.items():
            if fspec.get("required") and name not in data:
                raise WrapperError(f"missing required input: {name}")
            if name in data:
                self._validate_scalar(name, data[name], fspec.get("type", "any"))
        if not allow_extra:
            extra = set(data) - set(fields)
            if extra:
                raise WrapperError(f"unexpected input fields: {sorted(extra)}")

    @staticmethod
    def _validate_scalar(name: str, value: Any, expected: str) -> None:
        if expected == "any":
            return
        checks = {
            "string": lambda v: isinstance(v, str),
            "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
            "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
            "boolean": lambda v: isinstance(v, bool),
            "object": lambda v: isinstance(v, dict),
            "array": lambda v: isinstance(v, list),
        }
        if expected not in checks or not checks[expected](value):
            raise WrapperError(f"input {name!r} must be {expected}")

    def _invoke(self, request: Mapping[str, Any]) -> Dict[str, Any]:
        oid = request["operation_id"]
        op = self.operations[oid]
        adapter = op["adapter"]
        context = {
            "request_id": request["request_id"],
            "provenance": dict(request.get("provenance", {})),
            "authority_context": dict(request.get("authority_context", {})),
            "options": dict(request.get("options", {})),
        }
        if adapter["type"] == "native":
            handler = self._native_handlers.get(oid)
            if handler is None:
                raise WrapperError(f"native handler not registered for {oid}")
            result = handler(request["input"], context)
            outcome = result.pop("wrapper_outcome", "SUCCESS")
            if outcome not in OUTCOMES:
                raise WrapperError("native handler returned invalid wrapper_outcome")
            return self._response(request["request_id"], outcome, operation_id=oid, result=result, evidence=[{"level": "observed", "source": "native_handler"}])
        return self._invoke_legacy(op, request, context)

    def _invoke_legacy(self, op: Mapping[str, Any], request: Mapping[str, Any], context: Mapping[str, Any]) -> Dict[str, Any]:
        adapter = op["adapter"]
        exe = adapter["executable"]
        if not os.path.isfile(exe):
            raise WrapperError(f"executable does not exist: {exe}")
        argv = [exe]
        data = request["input"]
        for item in adapter.get("argv", []):
            if "literal" in item:
                argv.append(str(item["literal"]))
                continue
            name = item.get("param")
            if not name:
                raise WrapperError("argv item requires literal or param")
            present = name in data
            if item.get("required") and not present:
                raise WrapperError(f"missing required argv param: {name}")
            if not present:
                continue
            if "flag" in item:
                if data[name]:
                    argv.append(str(item["flag"]))
            else:
                argv.append(str(data[name]))

        env: Dict[str, str] = {}
        for key in adapter.get("inherit_env", []):
            if key in os.environ:
                env[str(key)] = os.environ[key]
        for key, value in adapter.get("env", {}).items():
            env[str(key)] = str(value)

        stdin_text = None
        stdin_param = adapter.get("stdin_param")
        if stdin_param is not None and stdin_param in data:
            value = data[stdin_param]
            stdin_text = value if isinstance(value, str) else json.dumps(value, separators=(",", ":"))

        timeout_ms = int(context.get("options", {}).get("timeout_ms", adapter.get("timeout_ms", 30000)))
        try:
            cp = subprocess.run(
                argv,
                input=stdin_text,
                text=True,
                capture_output=True,
                env=env,
                shell=False,
                timeout=timeout_ms / 1000.0,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raw = {"exit_code": None, "stdout": exc.stdout or "", "stderr": exc.stderr or "", "timed_out": True}
            return self._response(request["request_id"], "ABORTED", operation_id=op["operation_id"], raw=raw, diagnostics=[{"type": "timeout", "timeout_ms": timeout_ms}], evidence=[{"level": "observed", "source": "legacy_cli_adapter"}])
        except OSError as exc:
            raise WrapperError(f"process launch failed: {exc}") from exc

        raw = RawResult(cp.returncode, cp.stdout, cp.stderr)
        result = self._normalize_output(adapter, raw)
        outcome = self._normalize_outcome(adapter, raw)
        return self._response(request["request_id"], outcome, operation_id=op["operation_id"], result=result, raw=raw.as_dict(), evidence=[{"level": "observed", "source": "legacy_cli_adapter"}])

    @staticmethod
    def _normalize_output(adapter: Mapping[str, Any], raw: RawResult) -> Any:
        mode = adapter.get("stdout", "text")
        if mode == "text":
            return {"stdout": raw.stdout}
        if mode == "json":
            if not raw.stdout.strip():
                return None
            try:
                return json.loads(raw.stdout)
            except json.JSONDecodeError as exc:
                raise WrapperError(f"program stdout was declared JSON but was invalid: {exc}") from exc
        if mode == "lines":
            return {"lines": raw.stdout.splitlines()}
        raise WrapperError(f"unsupported stdout mode: {mode}")

    @staticmethod
    def _normalize_outcome(adapter: Mapping[str, Any], raw: RawResult) -> str:
        mapping = adapter.get("exit_map", {})
        key = str(raw.exit_code)
        outcome = mapping.get(key)
        if outcome is None:
            outcome = "SUCCESS" if raw.exit_code == 0 else "FAILED"
        if outcome not in OUTCOMES:
            raise WrapperError(f"invalid normalized outcome: {outcome}")
        return outcome

    def _describe(self) -> Dict[str, Any]:
        return {
            "program": self.manifest["program"],
            "manifest_version": self.manifest["manifest_version"],
            "protocol": PROTOCOL,
            "operation_count": len(self.operations),
            "separation": {
                "authority_grant": False,
                "safety_policy": False,
                "bitcode_verifier": False,
                "catalog": False,
            },
        }

    @staticmethod
    def _public_operation(op: Mapping[str, Any]) -> Dict[str, Any]:
        return {k: op[k] for k in ("operation_id", "alias", "evidence_level", "input", "side_effects") if k in op}

    def _ok(self, request_id: str, result: Any) -> Dict[str, Any]:
        return self._response(request_id, "SUCCESS", result=result)

    @staticmethod
    def _response(request_id: str, outcome: str, *, operation_id: Optional[str] = None, result: Any = None, raw: Any = None, diagnostics: Optional[list] = None, evidence: Optional[list] = None) -> Dict[str, Any]:
        return {
            "protocol": PROTOCOL,
            "request_id": request_id,
            "wrapper_outcome": outcome,
            "operation_id": operation_id,
            "result": result,
            "raw": raw,
            "diagnostics": diagnostics or [],
            "evidence": evidence or [],
        }
