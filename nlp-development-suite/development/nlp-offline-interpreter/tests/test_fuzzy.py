from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import random
import sys
import unittest

from jsonschema import Draft202012Validator


SUITE_ROOT = Path(__file__).resolve().parents[3]
PROJECTS = SUITE_ROOT / "projects"
PACKAGE_SRC = Path(__file__).resolve().parents[1] / "src"
for path in (PACKAGE_SRC, PROJECTS / "lexicon-core" / "src", PROJECTS / "natural-language-front-end"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from nlp_offline_interpreter.core import (  # noqa: E402
    InterpretationCandidate,
    InterpretationRequest,
    Interpreter,
    LayerResult,
    canonical_json,
)
from nlp_offline_interpreter.integration import interpret_text  # noqa: E402


SEED = 20261001
ALPHABET = (
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "
    "\t\r\n.,;:!?/\\[]{}()'\"-_+=*&#@%\x00"
    "αβγ漢字é\u0301🙂\u200f\ud800"
)


def random_text(rng: random.Random, maximum: int) -> str:
    return "".join(rng.choice(ALPHABET) for _ in range(rng.randrange(maximum + 1)))


class LooseAndFuzzyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        schema_path = Path(__file__).resolve().parents[1] / "schemas" / "generic-interpretation-v1.schema.json"
        cls.validator = Draft202012Validator(json.loads(schema_path.read_text(encoding="utf-8")))

    def test_seeded_generic_text_fuzz_is_deterministic_and_schema_valid(self):
        rng = random.Random(SEED)
        interpreter = Interpreter((), max_source_chars=1024)
        for index in range(5_000):
            with self.subTest(index=index):
                source = random_text(rng, 1100)
                first = interpreter.interpret(source, metadata={"case": index, "seed": SEED})
                second = interpreter.interpret(source, metadata={"seed": SEED, "case": index})
                rendered = canonical_json(first)
                self.assertEqual(rendered, canonical_json(second))
                payload = json.loads(rendered)
                self.validator.validate(payload)
                self.assertFalse(payload["execution_allowed"])
                self.assertEqual("NONE", payload["authority_effect"])
                self.assertEqual(
                    sha256(source.encode("utf-8", errors="surrogatepass")).hexdigest(),
                    payload["source_sha256"],
                )

    def test_loose_natural_language_variants_never_gain_authority(self):
        stems = [
            "find files named report in .",
            "define otter",
            "I feel uncertain",
            "flibbertigibbet",
            "show this",
        ]
        variants: list[str] = []
        for stem in stems:
            variants.extend(
                (stem, stem.upper(), f"  {stem}  ", f"{stem}!!!", stem.replace(" ", "\t"))
            )
        for index, source in enumerate(variants):
            with self.subTest(index=index, source=source):
                first = interpret_text(source, use_wordnet=False, mode="collect_all")
                second = interpret_text(source, use_wordnet=False, mode="collect_all")
                self.assertEqual(canonical_json(first), canonical_json(second))
                self.validator.validate(first.to_dict())
                self.assertFalse(first.to_dict()["execution_allowed"])

    def test_seeded_json_metadata_fuzz_round_trips_without_aliasing(self):
        rng = random.Random(SEED + 1)
        interpreter = Interpreter(())
        for index in range(1_000):
            metadata = {
                "index": index,
                "flag": bool(index % 2),
                "values": [rng.randrange(-10000, 10001), rng.random(), None],
                "text": random_text(rng, 80),
            }
            request = InterpretationRequest("probe", metadata)
            result = interpreter.interpret("probe", metadata=metadata)
            metadata["values"][0] = "mutated"
            self.assertNotEqual("mutated", result.to_dict()["metadata"]["values"][0])
            self.assertEqual(request.source_sha256, result.source_sha256)

    def test_hostile_text_fuzz_through_real_adapters_is_contained(self):
        rng = random.Random(SEED + 2)
        for index in range(1_000):
            with self.subTest(index=index):
                source = random_text(rng, 256)
                result = interpret_text(source, use_wordnet=False, mode="collect_all")
                payload = json.loads(canonical_json(result))
                self.validator.validate(payload)
                self.assertFalse(payload["execution_allowed"])

    def test_malformed_provider_fuzz_becomes_visible_trace(self):
        class Provider:
            layer_id = "fuzz-provider"
            layer_version = "1"

            def __init__(self, case: int) -> None:
                self.case = case

            def interpret(self, request):
                mode = self.case % 6
                if mode == 0:
                    return None
                if mode == 1:
                    raise RuntimeError("provider\n" + "x" * 5000)
                if mode == 2:
                    return LayerResult("wrong-provider", "1", "no_match")
                if mode == 3:
                    return LayerResult(
                        self.layer_id, self.layer_version, "no_match", diagnostics=("bad\ntext",)
                    )
                if mode == 4:
                    duplicate = InterpretationCandidate(
                        "duplicate", "inspect", {}, self.layer_id, "fixture"
                    )
                    return LayerResult(
                        self.layer_id,
                        self.layer_version,
                        "collision",
                        (duplicate, duplicate),
                    )
                return LayerResult(self.layer_id, self.layer_version, "no_match")

        for index in range(600):
            result = Interpreter((Provider(index),)).interpret("probe")
            rendered = canonical_json(result)
            payload = json.loads(rendered)
            self.validator.validate(payload)
            self.assertEqual("unparsed", result.status)
            expected = "no_match" if index % 6 == 5 else "error"
            self.assertEqual(expected, result.layer_trace[0].status)


if __name__ == "__main__":
    unittest.main()
