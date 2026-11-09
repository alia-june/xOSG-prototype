from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import json
from pathlib import Path
import sys
import time
import unittest


SUITE_ROOT = Path(__file__).resolve().parents[3]
PACKAGE_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from nlp_offline_interpreter.core import (  # noqa: E402
    MAX_JSON_DEPTH,
    MAX_JSON_ITEMS,
    MAX_LAYER_CANDIDATES,
    MAX_LAYERS,
    InterpretationCandidate,
    InterpretationRequest,
    Interpreter,
    LayerResult,
    canonical_json,
)


@dataclass(frozen=True)
class StaticLayer:
    layer_id: str
    layer_version: str
    result: LayerResult

    def interpret(self, request: InterpretationRequest) -> LayerResult:
        return self.result


class TortureTests(unittest.TestCase):
    def test_source_length_boundaries_and_large_whitespace(self):
        interpreter = Interpreter((), max_source_chars=16_384)
        self.assertEqual("unparsed", interpreter.interpret("x" * 16_384).status)
        self.assertEqual("invalid_input", interpreter.interpret("x" * 16_385).status)
        self.assertEqual("invalid_input", interpreter.interpret(" " * 16_384).status)

    def test_maximum_layer_trace_and_candidate_cardinality(self):
        empty_layers = tuple(
            StaticLayer(f"layer-{index}", "1", LayerResult(f"layer-{index}", "1", "no_match"))
            for index in range(MAX_LAYERS)
        )
        result = Interpreter(empty_layers, mode="collect_all").interpret("probe")
        self.assertEqual(MAX_LAYERS, len(result.layer_trace))
        candidates = tuple(
            InterpretationCandidate(
                f"candidate-{index}", "generic.inspect", {"index": index}, "bulk", "fixture"
            )
            for index in range(MAX_LAYER_CANDIDATES)
        )
        bulk = StaticLayer("bulk", "1", LayerResult("bulk", "1", "collision", candidates))
        result = Interpreter((bulk,), mode="collect_all").interpret("probe")
        self.assertEqual(MAX_LAYER_CANDIDATES, len(result.candidates))
        self.assertEqual("collision", json.loads(canonical_json(result))["status"])

    def test_json_item_and_depth_boundaries_fail_closed(self):
        InterpretationRequest("probe", {str(index): index for index in range(MAX_JSON_ITEMS - 1)})
        with self.assertRaisesRegex(ValueError, "item bound"):
            InterpretationRequest("probe", {str(index): index for index in range(MAX_JSON_ITEMS)})
        value: object = "leaf"
        # The metadata object occupies depth zero and its value occupies depth one.
        for _ in range(MAX_JSON_DEPTH - 1):
            value = [value]
        InterpretationRequest("probe", {"value": value})
        value = [value]
        with self.assertRaisesRegex(ValueError, "depth bound"):
            InterpretationRequest("probe", {"value": value})

    def test_repeated_and_concurrent_calls_are_stable(self):
        interpreter = Interpreter(())
        expected = canonical_json(interpreter.interpret("concurrency probe"))
        started = time.monotonic()
        for _ in range(50_000):
            self.assertEqual(expected, canonical_json(interpreter.interpret("concurrency probe")))
        with ThreadPoolExecutor(max_workers=8) as pool:
            outputs = list(
                pool.map(lambda _: canonical_json(interpreter.interpret("concurrency probe")), range(5_000))
            )
        self.assertTrue(all(item == expected for item in outputs))
        self.assertLess(time.monotonic() - started, 15.0)


if __name__ == "__main__":
    unittest.main()
