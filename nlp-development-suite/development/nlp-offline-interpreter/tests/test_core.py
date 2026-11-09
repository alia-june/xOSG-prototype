from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator

from nlp_offline_interpreter.core import (
    MAX_DIAGNOSTIC_CHARS,
    MAX_LAYER_CANDIDATES,
    MAX_LAYERS,
    InterpretationCandidate,
    InterpretationRequest,
    InterpretationResult,
    Interpreter,
    LayerResult,
    LayerTrace,
    SourceSpan,
    UnresolvedRegion,
    canonical_json,
)


@dataclass
class StaticLayer:
    layer_id: str
    layer_version: str
    result: LayerResult
    calls: int = 0

    def interpret(self, request: InterpretationRequest) -> LayerResult:
        self.calls += 1
        return self.result


@dataclass
class FailingLayer:
    layer_id: str = "failing"
    layer_version: str = "1"

    def interpret(self, request: InterpretationRequest) -> LayerResult:
        raise RuntimeError("controlled failure")


def candidate(layer_id: str, candidate_id: str, operation: str = "example.inspect") -> InterpretationCandidate:
    return InterpretationCandidate(
        candidate_id,
        operation,
        {"value": "alpha"},
        layer_id,
        "deterministic_rule",
        ("fixture",),
        (SourceSpan(0, 5, "fixture"),),
        {"value": 1, "semantics": "fixture only"},
    )


class GenericInterpreterTests(unittest.TestCase):
    def test_first_candidate_stops_lower_layers_visibly(self):
        first = StaticLayer(
            "first",
            "1",
            LayerResult("first", "1", "candidates", (candidate("first", "c1"),)),
        )
        second = StaticLayer("second", "1", LayerResult("second", "1", "no_match"))
        result = Interpreter((first, second)).interpret("alpha")
        self.assertEqual("parsed_single", result.status)
        self.assertEqual(1, first.calls)
        self.assertEqual(0, second.calls)
        self.assertEqual("not_consulted", result.layer_trace[1].status)
        self.assertFalse(result.to_dict()["execution_allowed"])

    def test_collect_all_preserves_order_and_collision(self):
        first = StaticLayer(
            "first",
            "1",
            LayerResult("first", "1", "candidates", (candidate("first", "c1"),)),
        )
        second = StaticLayer(
            "second",
            "2",
            LayerResult(
                "second",
                "2",
                "candidates",
                (candidate("second", "c2", "other.inspect"),),
            ),
        )
        result = Interpreter((first, second), mode="collect_all").interpret("alpha")
        self.assertEqual("collision", result.status)
        self.assertEqual(["c1", "c2"], [item.candidate_id for item in result.candidates])
        self.assertTrue(all(not item.to_dict()["execution_allowed"] for item in result.candidates))

    def test_partial_result_preserves_unresolved_region(self):
        layer = StaticLayer(
            "partial",
            "1",
            LayerResult(
                "partial",
                "1",
                "partial",
                (candidate("partial", "c1"),),
                (UnresolvedRegion(5, 10, "unsupported suffix", "partial"),),
            ),
        )
        result = Interpreter((layer,)).interpret("alpha beta")
        self.assertEqual("partial", result.status)
        self.assertEqual("unsupported suffix", result.unresolved[0].reason)

    def test_layer_error_is_visible_and_fallback_continues(self):
        fallback = StaticLayer(
            "fallback",
            "1",
            LayerResult(
                "fallback", "1", "candidates", (candidate("fallback", "fallback:c1"),)
            ),
        )
        result = Interpreter((FailingLayer(), fallback)).interpret("alpha")
        self.assertEqual("parsed_single", result.status)
        self.assertEqual("error", result.layer_trace[0].status)
        self.assertIn("controlled failure", result.layer_trace[0].diagnostics[0])
        self.assertEqual(1, fallback.calls)

    def test_layer_local_no_match_does_not_downgrade_successful_fallback(self):
        first = StaticLayer(
            "first",
            "1",
            LayerResult(
                "first",
                "1",
                "no_match",
                unresolved=(UnresolvedRegion(0, 5, "not recognized here", "first"),),
            ),
        )
        fallback = StaticLayer(
            "fallback",
            "1",
            LayerResult(
                "fallback", "1", "candidates", (candidate("fallback", "fallback:c1"),)
            ),
        )
        result = Interpreter((first, fallback)).interpret("alpha")
        self.assertEqual("parsed_single", result.status)
        self.assertEqual((), result.unresolved)
        self.assertEqual("no_match", result.layer_trace[0].status)

    def test_invalid_input_is_typed_and_hashed(self):
        result = Interpreter((), max_source_chars=5).interpret("too long")
        self.assertEqual("invalid_input", result.status)
        self.assertEqual(sha256(b"too long").hexdigest(), result.source_sha256)
        self.assertEqual("NONE", result.to_dict()["authority_effect"])

    def test_invalid_provider_span_becomes_layer_error(self):
        bad = InterpretationCandidate(
            "bad:c1",
            "example.inspect",
            {},
            "bad",
            "fixture",
            spans=(SourceSpan(0, 99),),
        )
        layer = StaticLayer("bad", "1", LayerResult("bad", "1", "candidates", (bad,)))
        result = Interpreter((layer,)).interpret("short")
        self.assertEqual("unparsed", result.status)
        self.assertEqual("error", result.layer_trace[0].status)

    def test_inconsistent_layer_status_becomes_visible_error(self):
        layer = StaticLayer("bad", "1", LayerResult("bad", "1", "collision"))
        result = Interpreter((layer,)).interpret("short")
        self.assertEqual("unparsed", result.status)
        self.assertEqual("error", result.layer_trace[0].status)
        self.assertIn("at least two candidates", result.layer_trace[0].diagnostics[0])

    def test_non_mapping_candidate_arguments_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "arguments must be a mapping"):
            InterpretationCandidate(
                "bad:c1",
                "example.inspect",
                ["not", "a", "mapping"],  # type: ignore[arg-type]
                "bad",
                "fixture",
            )

    def test_nested_inputs_are_detached_and_immutable(self):
        metadata = {"nested": {"items": ["original"]}}
        arguments = {"nested": {"items": ["original"]}}
        item = InterpretationCandidate(
            "safe:c1", "example.inspect", arguments, "safe", "fixture"
        )
        layer = StaticLayer(
            "safe", "1", LayerResult("safe", "1", "candidates", (item,))
        )
        result = Interpreter((layer,)).interpret("alpha", metadata=metadata)
        metadata["nested"]["items"][0] = "mutated"
        arguments["nested"]["items"][0] = "mutated"
        output = result.to_dict()
        self.assertEqual("original", output["metadata"]["nested"]["items"][0])
        self.assertEqual(
            "original", output["candidates"][0]["arguments"]["nested"]["items"][0]
        )
        with self.assertRaises(TypeError):
            result.metadata["new"] = "blocked"  # type: ignore[index]

    def test_boolean_offsets_and_bounds_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "offsets must be integers"):
            SourceSpan(False, 1)
        with self.assertRaisesRegex(ValueError, "positive integer"):
            Interpreter((), max_source_chars=True)

    def test_direct_public_objects_reject_forged_invariants(self):
        with self.assertRaisesRegex(ValueError, "candidate_id"):
            InterpretationCandidate("bad\n", "inspect", {}, "layer", "fixture")
        with self.assertRaisesRegex(ValueError, "trace status"):
            LayerTrace("layer", "1", "invented", 0, 0)
        with self.assertRaisesRegex(ValueError, "source_sha256"):
            InterpretationResult("alpha", "0" * 64, 5, "unparsed", (), (), ())
        digest = sha256(b"alpha").hexdigest()
        with self.assertRaisesRegex(ValueError, "parsed_single"):
            InterpretationResult("alpha", digest, 5, "parsed_single", (), (), ())
        with self.assertRaisesRegex(ValueError, "requires an unresolved"):
            InterpretationResult("alpha", digest, 5, "unparsed", (), (), ())

    def test_direct_result_rejects_candidate_trace_mismatch(self):
        item = candidate("layer", "candidate")
        digest = sha256(b"alpha").hexdigest()
        with self.assertRaisesRegex(ValueError, "layer trace"):
            InterpretationResult("alpha", digest, 5, "parsed_single", (item,), (), ())

    def test_layer_identity_is_frozen_at_interpreter_construction(self):
        class MutatingLayer:
            layer_id = "original"
            layer_version = "1"

            def interpret(self, request):
                self.layer_id = "changed"
                return LayerResult("changed", "1", "no_match")

        layer = MutatingLayer()
        result = Interpreter((layer,)).interpret("alpha")
        self.assertEqual("original", result.layer_trace[0].layer_id)
        self.assertEqual("error", result.layer_trace[0].status)

    def test_layer_and_provider_collections_must_be_finite_sequences(self):
        with self.assertRaisesRegex(TypeError, "finite sequence"):
            Interpreter(iter(()))  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "evidence must be a sequence"):
            InterpretationCandidate(
                "candidate", "inspect", {}, "layer", "fixture", (item for item in ())
            )

    def test_oversized_metadata_key_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "object key exceeds"):
            InterpretationRequest("alpha", {"k" * 65537: "value"})

    def test_provider_error_is_control_safe_and_bounded(self):
        class LoudLayer:
            layer_id = "loud"
            layer_version = "1"

            def interpret(self, request):
                raise RuntimeError("secret\n" + ("x" * (MAX_DIAGNOSTIC_CHARS * 2)))

        result = Interpreter((LoudLayer(),)).interpret("alpha")
        diagnostic = result.layer_trace[0].diagnostics[0]
        self.assertLessEqual(len(diagnostic), MAX_DIAGNOSTIC_CHARS)
        self.assertNotIn("\n", diagnostic)

    def test_provider_cardinality_and_layer_count_are_bounded(self):
        candidates = tuple(
            InterpretationCandidate(
                f"many:{index}", "example.inspect", {}, "many", "fixture"
            )
            for index in range(MAX_LAYER_CANDIDATES + 1)
        )
        result = Interpreter(
            (StaticLayer("many", "1", LayerResult("many", "1", "candidates", candidates)),)
        ).interpret("alpha")
        self.assertEqual("error", result.layer_trace[0].status)
        layers = tuple(
            StaticLayer(f"layer-{index}", "1", LayerResult(f"layer-{index}", "1", "no_match"))
            for index in range(MAX_LAYERS + 1)
        )
        with self.assertRaisesRegex(ValueError, "layer count"):
            Interpreter(layers)

    def test_lone_surrogate_is_hashed_and_serialized_without_crashing(self):
        value = "prefix\ud800suffix"
        result = Interpreter(()).interpret(value)
        rendered = canonical_json(result)
        self.assertIn("\\ud800", rendered)
        self.assertEqual(rendered, canonical_json(Interpreter(()).interpret(value)))

    def test_canonical_json_is_byte_stable(self):
        layer = StaticLayer(
            "first",
            "1",
            LayerResult("first", "1", "candidates", (candidate("first", "c1"),)),
        )
        interpreter = Interpreter((layer,))
        first = canonical_json(interpreter.interpret("alpha", metadata={"b": 2, "a": 1}))
        second = canonical_json(interpreter.interpret("alpha", metadata={"a": 1, "b": 2}))
        self.assertEqual(first, second)

    def test_result_schema_is_valid_and_accepts_fixture(self):
        schema_path = Path(__file__).resolve().parents[1] / "schemas" / "generic-interpretation-v1.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        layer = StaticLayer(
            "first",
            "1",
            LayerResult("first", "1", "candidates", (candidate("first", "c1"),)),
        )
        result = Interpreter((layer,)).interpret("alpha").to_dict()
        Draft202012Validator(schema).validate(result)


if __name__ == "__main__":
    unittest.main()
