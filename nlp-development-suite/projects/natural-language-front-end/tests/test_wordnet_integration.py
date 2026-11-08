import unittest

from grammar_parser import parse
from wordnet_lexicon import WordNetLexicon


class WordNetIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.lexicon = WordNetLexicon()
        except RuntimeError as exc:
            raise unittest.SkipTest(str(exc)) from exc

    def test_wordnet_expands_noun_and_adjective_vocabulary(self):
        result = parse("the curious otter runs", use_wordnet=True)
        self.assertTrue(result["accepted"])
        self.assertEqual(result["wordnet_release"], "oewn:2025")
        evidence = {entry["text"]: entry for entry in result["lexical_evidence"]}
        self.assertEqual(evidence["otter"]["manual_categories"], [])
        self.assertIn("N", evidence["otter"]["grammar_categories"])
        self.assertIn("ADJ", evidence["curious"]["grammar_categories"])
        self.assertEqual(evidence["the"]["grammar_categories"], ["DET"])

    def test_senses_are_candidates_and_not_selected(self):
        result = parse("the otter runs", use_wordnet=True, include_senses=True)
        evidence = {entry["text"]: entry for entry in result["lexical_evidence"]}
        self.assertGreater(len(evidence["otter"]["sense_candidates"]), 0)
        self.assertNotIn("sense", result["trees"][0])

    def test_wordnet_does_not_invent_verb_frames(self):
        result = parse("the otter thinks", use_wordnet=True)
        self.assertFalse(result["accepted"])

    def test_complete_release_inventory(self):
        inventory = self.lexicon.inventory()
        self.assertTrue(inventory["complete"])
        self.assertEqual(inventory["counts"],
                         {"words": 135969, "synsets": 107519, "senses": 185129})

    def test_definitions_keep_all_senses_unselected(self):
        definitions = self.lexicon.definitions("dog")
        self.assertGreater(len(definitions), 1)
        first = next(item for item in definitions if item["id"] == "oewn-02086723-n")
        self.assertIn("dog", first["lemmas"])
        self.assertIn("domesticated", first["definition"])

    def test_semantic_and_lexical_relations_are_reported(self):
        dog = self.lexicon.relations("dog")
        domestic = next(item for item in dog["senses"] if item["id"] == "oewn-02086723-n")
        self.assertIn("hypernym", domestic["semantic_relations"])
        self.assertGreater(domestic["semantic_relations"]["hypernym"]["target_count"], 0)
        good = self.lexicon.relations("good")
        relation_names = {name for entry in good["lexical_relations"]
                          for name in entry["relations"]}
        self.assertIn("antonym", relation_names)


if __name__ == "__main__":
    unittest.main()
