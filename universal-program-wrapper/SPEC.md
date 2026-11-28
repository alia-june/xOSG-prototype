# UPW Protocol Specification v0.1

## Request envelope

```json
{
  "protocol": "upw/0.1",
  "request_id": "R-123",
  "kind": "invoke",
  "operation_id": "F008",
  "input": {},
  "provenance": {},
  "authority_context": {},
  "options": {
    "timeout_ms": 5000
  }
}
```

Only `invoke` requires `operation_id`. Introspection requests use `kind` only.

## Response envelope

```json
{
  "protocol": "upw/0.1",
  "request_id": "R-123",
  "wrapper_outcome": "SUCCESS",
  "operation_id": "F008",
  "result": {},
  "raw": {
    "exit_code": 0,
    "stdout": "",
    "stderr": ""
  },
  "diagnostics": [],
  "evidence": []
}
```

## Wrapper outcomes

v0.1 uses:

- `SUCCESS`
- `NO_CHANGE`
- `PARTIAL`
- `FAILED`
- `ABORTED`
- `UNKNOWN`
- `WRAPPER_ERROR`

A program's numeric exit code is never discarded.

## Evidence levels

When a manifest or operation reports capability evidence it must use one of:

```text
declared
discovered
tested
observed
attested
```

No automatic promotion occurs.

## Legacy argument templates

Each argument specification is either:

```json
{"literal": "--flag"}
```

or:

```json
{"param": "name", "required": true}
```

or:

```json
{"param": "verbose", "flag": "--verbose"}
```

Parameter values are passed as individual argv elements. No shell command string is constructed.

## Environment

`adapter.env` contains explicit static environment entries. `adapter.inherit_env` lists names that may be copied from the parent environment. Everything else is absent from the child environment.

## Authority

`authority_context` is opaque application data to UPW v0.1. UPW preserves it in the request context for policy layers/adapters, but does not treat it as authorization.
