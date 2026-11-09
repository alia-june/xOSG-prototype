"""Copy the validated alias catalog into the static File Atlas build."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "command_aliases.json"
DATA = ROOT / "dist" / "data"


def main() -> None:
    raw = SOURCE.read_bytes()
    if len(raw) > 64 * 1024:
        raise RuntimeError("Alias catalog exceeds the 64 KiB bound")
    document = json.loads(raw.decode("utf-8"))
    if document.get("schema_version") != "omni-alias/0.1":
        raise RuntimeError("Unexpected alias catalog version")
    rules = document.get("rules")
    if not isinstance(rules, list) or not 0 < len(rules) <= 200:
        raise RuntimeError("Unexpected alias rule count")

    DATA.mkdir(parents=True, exist_ok=True)
    compact = json.dumps(document, ensure_ascii=False, separators=(",", ":"))
    (DATA / "command_aliases.json").write_text(compact, encoding="utf-8")
    canonical_rules = json.dumps(rules, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    file_capabilities = {"help", "workspace", "list_files", "read_file", "find_files", "search_text"}
    manifest = {
        "schema": "file-atlas-data/1",
        "intent_schema": "omni-intent/0.4-browser",
        "alias_catalog_version": document["schema_version"],
        "rule_count": len(rules),
        "active_file_rule_count": sum(rule.get("capability") in file_capabilities for rule in rules),
        "source_sha256": sha256(raw).hexdigest(),
        "rules_sha256": sha256(canonical_rules.encode("utf-8")).hexdigest(),
    }
    (DATA / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
