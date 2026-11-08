"""Pinned Open English WordNet lookups for the grammar parser.

WordNet supplies possible word classes and senses. It does not identify the
correct sense in a sentence or specify this parser's verb argument rules.
"""

from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import Any


WORDNET_RELEASE = "oewn:2025"
DEFAULT_DATA_DIR = Path(__file__).resolve().parent / ".wn_data"
EXPECTED_WORDS = 135_969
EXPECTED_SYNSETS = 107_519
EXPECTED_SENSES = 185_129
MAX_RELATION_TARGETS = 50


class WordNetLexicon:
    def __init__(self, data_dir: Path | None = None):
        try:
            import wn
            from wn.morphy import Morphy
        except ImportError as exc:
            raise RuntimeError("Install wn==1.1.1 before using --wordnet.") from exc

        data_dir = data_dir or DEFAULT_DATA_DIR
        if not data_dir.is_dir():
            raise RuntimeError(
                f"WordNet data is missing at {data_dir}. "
                f"Run: python -m wn --dir \"{data_dir}\" download {WORDNET_RELEASE}"
            )
        wn.config.data_directory = str(data_dir)
        self.wordnet = wn.Wordnet(WORDNET_RELEASE, lemmatizer=Morphy())
        if not any(f"{lex.id}:{lex.version}" == WORDNET_RELEASE for lex in self.wordnet.lexicons()):
            raise RuntimeError(
                f"{WORDNET_RELEASE} is not installed at {data_dir}. "
                f"Run: python -m wn --dir \"{data_dir}\" download {WORDNET_RELEASE}"
            )

    @cache
    def parts_of_speech(self, form: str) -> tuple[str, ...]:
        return tuple(sorted({word.pos for word in self.wordnet.words(form)}))

    def grammar_categories(self, form: str) -> frozenset[str]:
        pos = self.parts_of_speech(form)
        categories = set()
        if "n" in pos:
            categories.add("N")
        if "a" in pos or "s" in pos:
            categories.add("ADJ")
        return frozenset(categories)

    @cache
    def verb_synset_ids(self, form: str) -> tuple[str, ...]:
        """Possible verb senses; equality is lexical evidence, not intent."""
        return tuple(sorted({synset.id for synset in self.wordnet.synsets(form, pos="v")}))

    @cache
    def sense_candidates(self, form: str) -> tuple[dict[str, Any], ...]:
        """Return candidates without selecting a context-specific meaning."""
        return tuple(
            {"id": synset.id, "pos": synset.pos, "definition": synset.definition()}
            for synset in sorted(self.wordnet.synsets(form), key=lambda item: item.id)
        )

    @cache
    def definitions(self, form: str) -> tuple[dict[str, Any], ...]:
        """Return every synset candidate and definition; do not choose a sense."""
        return tuple(self._synset_record(synset) for synset in self._synsets(form))

    @cache
    def relations(self, form: str) -> dict[str, Any]:
        """Return semantic and lexical relations for every candidate sense."""
        records = []
        for synset in self._synsets(form):
            semantic = {}
            for relation, targets in sorted(synset.relations().items()):
                ordered = sorted(targets, key=lambda item: item.id)
                semantic[relation] = {
                    "target_count": len(ordered),
                    "truncated": len(ordered) > MAX_RELATION_TARGETS,
                    "targets": [self._relation_synset(target)
                                for target in ordered[:MAX_RELATION_TARGETS]],
                }
            records.append({**self._synset_record(synset),
                            "semantic_relations": semantic})

        lexical = []
        seen_senses = set()
        for word in sorted(self.wordnet.words(form), key=lambda item: item.id):
            for sense in sorted(word.senses(), key=lambda item: item.id):
                if sense.id in seen_senses:
                    continue
                seen_senses.add(sense.id)
                relation_records = {}
                for relation, targets in sorted(sense.relations().items()):
                    ordered = sorted(targets, key=lambda item: item.id)
                    relation_records[relation] = {
                        "target_count": len(ordered),
                        "truncated": len(ordered) > MAX_RELATION_TARGETS,
                        "targets": [{"sense_id": target.id,
                                     "lemma": target.word().lemma(),
                                     "synset_id": target.synset().id}
                                    for target in ordered[:MAX_RELATION_TARGETS]],
                    }
                if relation_records:
                    lexical.append({"sense_id": sense.id, "lemma": word.lemma(),
                                    "synset_id": sense.synset().id,
                                    "relations": relation_records})
        return {"senses": records, "lexical_relations": lexical}

    def inventory(self) -> dict[str, Any]:
        """Report exact installed counts used by the completeness check."""
        counts = {"words": len(self.wordnet.words()),
                  "synsets": len(self.wordnet.synsets()),
                  "senses": len(self.wordnet.senses())}
        expected = {"words": EXPECTED_WORDS, "synsets": EXPECTED_SYNSETS,
                    "senses": EXPECTED_SENSES}
        return {"release": WORDNET_RELEASE, "counts": counts,
                "expected_counts": expected, "complete": counts == expected}

    def _synsets(self, form: str) -> tuple[Any, ...]:
        return tuple(sorted({synset.id: synset for synset in self.wordnet.synsets(form)}.values(),
                            key=lambda item: item.id))

    @staticmethod
    def _synset_record(synset: Any) -> dict[str, Any]:
        return {"id": synset.id, "pos": synset.pos,
                "lemmas": sorted(synset.lemmas(), key=str.casefold),
                "definition": synset.definition(), "examples": synset.examples()}

    @staticmethod
    def _relation_synset(synset: Any) -> dict[str, Any]:
        return {"id": synset.id, "pos": synset.pos,
                "lemmas": sorted(synset.lemmas(), key=str.casefold),
                "definition": synset.definition()}
