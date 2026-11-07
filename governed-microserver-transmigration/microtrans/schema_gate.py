"""One-capability JSON CLI microserver: candidate manifest shape validation."""
from .protocol import digest, serve
from .schema_validation import schema_faults


def check_schema(manifest):
    faults = schema_faults(manifest)
    if faults:
        return {"faults": faults,
                "data": {"kind": "sentinel", "code": "SENTINEL_ABSENT"},
                "input_sha256": digest(manifest)}
    # The application payload itself remains unchanged; only protocol framing differs.
    return {"faults": [], "data": manifest, "input_sha256": digest(manifest)}


if __name__ == "__main__":
    serve("schema-gate", check_schema)
