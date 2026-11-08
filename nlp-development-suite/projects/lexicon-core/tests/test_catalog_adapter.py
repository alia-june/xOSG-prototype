import json
from dataclasses import replace
from pathlib import Path
import unittest

from lexicon_core.adapters.catalog_v0_1 import (
    CAPABILITY_IDS,
    CatalogAdapter,
    CatalogOperationRegistry,
    validate_interpretation,
)


CATALOG_HANDOFF = {
    "handoff_id": "catalog.modular-nlp-capability-handoff/0.1",
    "current_operations": {
        "read": ["catalog.inbox", "catalog.ls", "catalog.show", "catalog.find", "catalog.project.inspect"],
        "proposal_only": ["catalog.collect", "catalog.relate", "catalog.file.move"],
    },
    "operation_contracts": {
        "catalog.inbox": {"required": {}, "optional": {}, "allow_extra": False},
        "catalog.ls": {"required": {"scope": "string"}, "optional": {}, "allow_extra": False},
        "catalog.show": {"required": {"object_id": "string"}, "optional": {}, "allow_extra": False},
        "catalog.find": {"required": {"term": "string"}, "optional": {}, "allow_extra": False},
        "catalog.project.inspect": {"required": {"project": "string"}, "optional": {}, "allow_extra": False},
        "catalog.collect": {
            "required": {"item": "string", "collection": "string"},
            "optional": {"physical_move": "boolean", "interpretation": "string"},
            "allow_extra": False,
        },
        "catalog.relate": {"required": {"source": "string", "target": "string"}, "optional": {}, "allow_extra": False},
        "catalog.file.move": {
            "required": {"item": "string", "destination": "string"},
            "optional": {"interpretation": "string"},
            "allow_extra": False,
        },
    },
}


class CatalogAdapterTests(unittest.TestCase):
    def setUp(self):
        self.registry = CatalogOperationRegistry.from_mapping(CATALOG_HANDOFF)
        self.adapter = CatalogAdapter(self.registry)

    def assert_valid(self, result):
        self.assertEqual(validate_interpretation(result, self.registry), ())
        json.dumps(result.to_dict())

    def test_find_preserves_exact_source_digest_and_span(self):
        result = self.adapter.interpret("find recovery")
        self.assertEqual(result.status, "parsed_single")
        self.assertEqual(result.candidates[0].operation, "catalog.find")
        self.assertEqual(result.candidates[0].source_spans[0].text, "recovery")
        self.assertEqual((result.candidates[0].source_spans[0].start, result.candidates[0].source_spans[0].end), (5, 13))
        self.assertEqual(result.module.capabilities, CAPABILITY_IDS)
        self.assert_valid(result)

    def test_read_acceptance_examples(self):
        cases = {
            "show inbox": ("catalog.inbox", {}),
            "show object abc123": ("catalog.show", {"object_id": "abc123"}),
            "inspect project MageCore": ("catalog.project.inspect", {"project": "MageCore"}),
        }
        for text, (operation, arguments) in cases.items():
            with self.subTest(text=text):
                result = self.adapter.interpret(text)
                self.assertEqual(result.status, "parsed_single")
                self.assertEqual(result.candidates[0].operation, operation)
                self.assertEqual(result.candidates[0].arguments, arguments)
                self.assert_valid(result)

    def test_ambiguous_move_preserves_both_meanings(self):
        result = self.adapter.interpret("move report into MageCore")
        self.assertEqual(result.status, "collision")
        self.assertEqual(
            {candidate.operation for candidate in result.candidates},
            {"catalog.collect", "catalog.file.move"},
        )
        self.assert_valid(result)

    def test_negative_physical_move_constraint_blocks_move_candidate(self):
        result = self.adapter.interpret("put report with MageCore, don't move the actual files")
        self.assertEqual(result.status, "parsed_single")
        self.assertEqual([candidate.operation for candidate in result.candidates], ["catalog.collect"])
        self.assertIs(result.candidates[0].arguments["physical_move"], False)
        self.assertEqual(result.candidates[0].constraints[0]["name"], "physical_move")
        self.assert_valid(result)

        variant = self.adapter.interpret("put report with MageCore without moving the actual files")
        self.assertEqual(variant.status, "parsed_single")
        self.assertEqual([candidate.operation for candidate in variant.candidates], ["catalog.collect"])
        self.assertIs(variant.candidates[0].arguments["physical_move"], False)
        self.assert_valid(variant)

    def test_unsupported_text_abstains_with_unresolved_span(self):
        result = self.adapter.interpret("please contemplate the archive")
        self.assertEqual(result.status, "unparsed")
        self.assertEqual(result.candidates, ())
        self.assertEqual(result.unresolved[0].text, "please contemplate the archive")
        self.assert_valid(result)

    def test_empty_input_is_invalid(self):
        result = self.adapter.interpret("   ")
        self.assertEqual(result.status, "invalid_input")
        self.assertEqual(result.candidates, ())
        self.assert_valid(result)

    def test_conflicting_constraints_are_explicit(self):
        result = self.adapter.interpret("put report with MageCore, don't move the actual files but also move the actual files")
        self.assertEqual(result.status, "conflict")
        self.assertEqual(len(result.unresolved), 2)
        self.assert_valid(result)

    def test_registry_gates_operations(self):
        registry = CatalogOperationRegistry("test/find-only", frozenset({"catalog.find"}))
        adapter = CatalogAdapter(registry)
        result = adapter.interpret("show inbox")
        self.assertEqual(result.status, "unparsed")
        self.assertEqual(result.candidates, ())
        self.assertIn("operation_not_in_registry:catalog.inbox", result.unresolved[0].reason)
        self.assertEqual(validate_interpretation(result, registry), ())

    def test_registry_supplied_argument_contracts_are_enforced(self):
        self.assertEqual(self.registry.validate_arguments("catalog.find", {}), ("missing:term",))
        self.assertEqual(
            self.registry.validate_arguments("catalog.find", {"term": 7}),
            ("type:term:string",),
        )
        invalid_registry = CatalogOperationRegistry.from_mapping(
            {
                "handoff_id": "test/invalid-find-contract",
                "current_operations": {"read": ["catalog.find"]},
                "operation_contracts": {
                    "catalog.find": {"required": {"term": "integer"}, "allow_extra": False}
                },
            }
        )
        result = CatalogAdapter(invalid_registry).interpret("find recovery")
        self.assertEqual(result.status, "unparsed")
        self.assertIn("invalid_arguments:catalog.find:type:term:integer", result.unresolved[0].reason)
        self.assertEqual(validate_interpretation(result, invalid_registry), ())

        valid = self.adapter.interpret("find recovery")
        forged = replace(valid, candidates=(replace(valid.candidates[0], arguments={}),))
        self.assertIn(
            "invalid_candidate_arguments:catalog.find:missing:term",
            validate_interpretation(forged, self.registry),
        )
        with self.assertRaises(TypeError):
            self.registry.argument_contracts["catalog.find"] = None
        with self.assertRaises(TypeError):
            self.registry.argument_contracts["catalog.find"].required["term"] = "integer"

    def test_generic_file_task_routes_through_catalog_profile(self):
        from lexicon_core.tasks import TaskRequest, built_in_modules, route_request

        request = TaskRequest("find files named report")
        routed = route_request(request, built_in_modules())
        result = self.adapter.interpret_task_route(request, routed)
        self.assertEqual(result.status, "parsed_single")
        self.assertEqual(result.candidates[0].operation, "catalog.find")
        self.assertEqual(result.candidates[0].arguments, {"term": "report"})
        self.assertEqual(result.candidates[0].origin_class, "ADAPTER_NORMALIZATION")
        self.assertEqual(result.layer_trace[0].layer_id, "generic-task-router")
        self.assert_valid(result)

    def test_partial_parse_keeps_candidate_and_unresolved_region(self):
        result = self.adapter.interpret("find recovery; explain why it matters")
        self.assertEqual(result.status, "parsed_single")
        self.assertEqual(result.candidates[0].arguments, {"term": "recovery"})
        self.assertEqual(result.unresolved[0].text, "explain why it matters")
        self.assertEqual(result.unresolved[0].reason, "unsupported_trailing_clause")
        self.assert_valid(result)

    def test_schema_is_valid_json(self):
        schema_dir = Path(__file__).parents[1] / "schemas"
        for name in ("catalog-interpretation-result-v0.1.schema.json", "catalog-operation-registry-v0.1.schema.json"):
            schema = json.loads((schema_dir / name).read_text(encoding="utf-8"))
            self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")

    def test_published_acceptance_fixture(self):
        fixture_path = Path(__file__).parents[1] / "examples" / "catalog-v0.1-acceptance.json"
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        self.assertEqual(fixture["contract_id"], "catalog.modular-nlp-capability-handoff/0.1")
        for case in fixture["cases"]:
            with self.subTest(text=case["input"]):
                result = self.adapter.interpret(case["input"])
                self.assertEqual(result.status, case["expected_status"])
                self.assertEqual(
                    [candidate.operation for candidate in result.candidates],
                    case["expected_operations"],
                )
                if "expected_arguments" in case:
                    for key, value in case["expected_arguments"].items():
                        self.assertEqual(result.candidates[0].arguments[key], value)
                self.assert_valid(result)


if __name__ == "__main__":
    unittest.main()
