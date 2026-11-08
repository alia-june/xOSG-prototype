import unittest

from lexicon_core.registry import inventory, load_registry, source_path
from lexicon_core.synthesis import synthesize
from lexicon_core.collisions import group_records
from lexicon_core.intent import parse_intent
from lexicon_core.morphology import describe_features
from lexicon_core.relations import traverse_relations
from lexicon_core.tasks import TaskRequest, built_in_modules, route_request


class RegistryTests(unittest.TestCase):
    def test_registry_exposes_all_sources(self):
        registry = load_registry()
        expected = {"oewn", "cmudict", "ipa_dict", "unimorph", "wiktionary", "gcide", "odict", "stardict-inbox"}
        self.assertTrue(expected.issubset(registry["sources"]))
        status = inventory()
        self.assertTrue(all(item["exists"] for item in status.values()))
        self.assertTrue(source_path("wiktionary").is_dir())


class SynthesisTests(unittest.TestCase):
    def test_context_reranks_without_merging(self):
        result = synthesize(
            "bank",
            [
                {"source": "Open English WordNet", "reference": "n-finance", "pos": "noun", "definition": "a financial institution that accepts deposits"},
                {"source": "Open English WordNet", "reference": "v-enclose", "pos": "verb", "definition": "enclose with a bank"},
                {"source": "GCIDE", "reference": "historical", "pos": "noun", "definition": "a bench or high seat"},
            ],
            "I deposited money at the bank",
        )
        self.assertEqual(result.ranked[0].reference, "n-finance")
        self.assertEqual(len(result.ranked), 3)
        self.assertIn("financial", result.ranked[0].definition)


class ModuleTests(unittest.TestCase):
    def test_collisions_remain_visible(self):
        groups = group_records([
            {"term": "bank", "source": "WordNet", "definition": "institution"},
            {"term": "BANK", "source": "GCIDE", "definition": "bench"},
        ])
        self.assertEqual(len(groups), 1)
        self.assertTrue(groups[0].collision)
        self.assertEqual(len(groups[0].records), 2)

    def test_relations_are_bounded(self):
        graph = {"a": [("b", "hypernym"), ("c", "hyponym")], "b": [("d", "related")], "c": [("e", "related")]}
        result = traverse_relations("a", graph, max_depth=2, per_level_limit=1, total_limit=2)
        self.assertEqual([node.node for node in result.nodes], ["b", "d"])
        self.assertTrue(result.truncated)

    def test_intent_is_proposal_only(self):
        proposal = parse_intent("find files named report")
        self.assertEqual(proposal.operation, "search")
        self.assertEqual(proposal.target, "files")
        self.assertEqual(proposal.query, "report")
        self.assertEqual(proposal.status, "proposal-only")

    def test_morphology_labels_are_deterministic(self):
        self.assertEqual(describe_features("V;PST;3"), ("verb", "past", "third person"))

    def test_task_router_preserves_module_matches(self):
        routed = route_request(TaskRequest("find files named report"), built_in_modules())
        self.assertEqual(routed.matches[0].module_id, "file-explorer")
        self.assertEqual(routed.results[0].proposals[0].fields["execute"], False)

    def test_expert_control_is_proposal_only(self):
        routed = route_request(TaskRequest("if the file exists then show it"), built_in_modules())
        proposal = next(result.proposals[0] for result in routed.results if result.module_id == "expert-control")
        self.assertEqual(proposal.operation, "propose-rule")
        self.assertEqual(proposal.status, "proposal-only")

    def test_eliza_nxt_is_deterministic(self):
        routed = route_request(TaskRequest("I feel uncertain"), built_in_modules())
        proposal = next(result.proposals[0] for result in routed.results if result.module_id == "eliza-nxt")
        self.assertEqual(proposal.fields["text"], "Why do you feel uncertain?")
        self.assertTrue(proposal.fields["deterministic"])


if __name__ == "__main__":
    unittest.main()
