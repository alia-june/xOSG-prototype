from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_source_map", ROOT / "validate_source_map.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SourceMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads((ROOT / "SOURCE_LANGUAGE_MAP.json").read_text(encoding="utf-8"))

    def test_current_map_passes(self):
        result = MODULE.validate(copy.deepcopy(self.data))
        self.assertEqual("passed", result["status"])
        self.assertGreaterEqual(result["sources"], 10)
        self.assertGreaterEqual(result["languages"], 10)

    def test_unknown_source_is_rejected(self):
        data = copy.deepcopy(self.data)
        data["languages"][0]["source_candidates"].append("invented-source")
        with self.assertRaisesRegex(ValueError, "unknown sources"):
            MODULE.validate(data)

    def test_contact_cannot_be_silently_relabeled_as_genealogy(self):
        data = copy.deepcopy(self.data)
        edge = next(
            item
            for item in data["relations"]
            if item["from"] == "anglo-norman" and item["to"] == "middle-english"
        )
        edge["kind"] = "genealogical_descent"
        with self.assertRaisesRegex(ValueError, "invalid relation kind"):
            MODULE.validate(data)

    def test_geist_must_remain_generated(self):
        data = copy.deepcopy(self.data)
        data["geist_definition"] = "A directly sourced cultural fact."
        with self.assertRaisesRegex(ValueError, "generated-only boundary"):
            MODULE.validate(data)

    def test_geist_must_remain_lowest_priority(self):
        data = copy.deepcopy(self.data)
        data["dimension_priority"].remove("GEIST")
        data["dimension_priority"].insert(0, "GEIST")
        with self.assertRaisesRegex(ValueError, "lowest-priority"):
            MODULE.validate(data)

    def test_aboutness_must_be_sense_scoped(self):
        data = copy.deepcopy(self.data)
        data["aboutness_definition"] = "A permanent subject label attached to a spelling."
        with self.assertRaisesRegex(ValueError, "sense-scoped"):
            MODULE.validate(data)

    def test_aboutness_truth_states_cannot_be_collapsed(self):
        data = copy.deepcopy(self.data)
        data["aboutness_truth_states"] = ["ACCEPTED_TOPIC_MAPPING"]
        with self.assertRaisesRegex(ValueError, "truth states"):
            MODULE.validate(data)

    def test_translation_dimension_is_explicit(self):
        self.assertIn("TRANSLATION_EQUIVALENCE", self.data["evidence_dimensions"])
        self.assertLess(
            self.data["dimension_priority"].index("TRANSLATION_EQUIVALENCE"),
            self.data["dimension_priority"].index("ABOUTNESS"),
        )

    def test_translation_source_license_boundaries(self):
        sources = {item["id"]: item for item in self.data["sources"]}
        self.assertEqual("admitted_for_mapping", sources["un-parallel-corpus-v1"]["admission_status"])
        self.assertEqual("admitted_for_mapping", sources["qcri-waw-corpus"]["admission_status"])
        self.assertEqual("isolated_adapter_only", sources["freedict-eng-hin-1.6"]["admission_status"])
        self.assertEqual("isolated_adapter_only", sources["freedict-eng-ara-0.6.3"]["admission_status"])
        for source_id in ("samanantar-0.3", "tdil-ilci-hin-eng", "wipo-pearl", "madar-parallel"):
            self.assertEqual("blocked", sources[source_id]["admission_status"])

    def test_unresolved_license_cannot_be_admitted(self):
        data = copy.deepcopy(self.data)
        source = next(item for item in data["sources"] if item["id"] == "samanantar-0.3")
        source["admission_status"] = "admitted_for_mapping"
        with self.assertRaisesRegex(ValueError, "unresolved license state"):
            MODULE.validate(data)

    def test_cross_linguistic_sources_have_bounded_admission(self):
        sources = {item["id"]: item for item in self.data["sources"]}
        for source_id in ("concepticon-3.4", "ids-cldf", "wold", "grambank"):
            self.assertEqual("admitted_for_mapping", sources[source_id]["admission_status"])
        self.assertEqual("isolated_adapter_only", sources["phoible-2.0"]["admission_status"])
        self.assertEqual("review_required", sources["universal-dependencies"]["admission_status"])

    def test_phonology_and_grammar_are_explicit_dimensions(self):
        self.assertIn("PHONOLOGY", self.data["evidence_dimensions"])
        self.assertIn("GRAMMAR", self.data["evidence_dimensions"])
        self.assertLess(
            self.data["dimension_priority"].index("GRAMMAR"),
            self.data["dimension_priority"].index("MEANING"),
        )

    def test_ingestion_authority_cannot_be_inferred(self):
        data = copy.deepcopy(self.data)
        data["content_ingestion_authorized"] = True
        with self.assertRaisesRegex(ValueError, "content ingestion"):
            MODULE.validate(data)


if __name__ == "__main__":
    unittest.main()
