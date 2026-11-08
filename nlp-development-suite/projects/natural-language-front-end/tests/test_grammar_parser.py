import unittest

from grammar_parser import parse


class GrammarParserTests(unittest.TestCase):
    def test_basic_sentence_and_offsets(self):
        text = "The red dog runs."
        result = parse(text)
        self.assertTrue(result["accepted"])
        self.assertEqual(len(result["trees"]), 1)
        self.assertEqual(result["tokens"][0], {"text": "The", "start": 0, "end": 3})
        self.assertEqual(result["trees"][0]["end"], text.index("."))

    def test_attachment_ambiguity_is_preserved(self):
        result = parse("I saw the man with the telescope")
        self.assertTrue(result["accepted"])
        self.assertEqual(len(result["trees"]), 2)
        self.assertNotEqual(result["trees"][0], result["trees"][1])

    def test_unknown_word_is_reported_without_guessing(self):
        result = parse("the quokka runs")
        self.assertFalse(result["accepted"])
        self.assertEqual(result["unknown_words"], ["quokka"])

    def test_known_words_can_still_fail_grammar(self):
        result = parse("the dog the cat")
        self.assertFalse(result["accepted"])
        self.assertNotIn("unknown_words", result)


if __name__ == "__main__":
    unittest.main()
