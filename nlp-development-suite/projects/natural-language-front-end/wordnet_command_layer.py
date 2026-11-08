"""Secondary, non-executing WordNet proposals for unmatched command verbs."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import re

from command_aliases import AliasRule, Candidate, resolve_aliases
from wordnet_lexicon import DEFAULT_DATA_DIR, WORDNET_RELEASE, WordNetLexicon


ANCHORS = ("find", "list", "read", "search", "show")


@lru_cache(maxsize=2)
def _lexicon(data_dir: Path) -> WordNetLexicon:
    return WordNetLexicon(data_dir)


def suggest_wordnet(source: str, rules: tuple[AliasRule, ...],
                    *, data_dir: Path = DEFAULT_DATA_DIR) -> tuple[Candidate, ...]:
    """Suggest commands through shared verb synsets; never select a sense."""
    command = source.strip()
    match = re.fullmatch(r"([A-Za-z]+)\s+(.+)", command)
    if match is None:
        return ()
    verb, remainder = match.groups()
    verb = verb.casefold()
    known_heads = {rule.phrase.split(" ", 1)[0].casefold() for rule in rules}
    if verb in known_heads:
        return ()
    lexicon = _lexicon(data_dir)
    source_ids = set(lexicon.verb_synset_ids(verb))
    if not source_ids:
        return ()
    best: dict[tuple[str, tuple[tuple[str, str], ...]], Candidate] = {}
    for anchor in ANCHORS:
        shared = sorted(source_ids.intersection(lexicon.verb_synset_ids(anchor)))
        if not shared:
            continue
        substituted = f"{anchor} {remainder}"
        direct = resolve_aliases(substituted, rules)
        for candidate in direct.candidates:
            # A transformed phrase must actually use the anchor that WordNet linked.
            phrase = next((rule.phrase for rule in rules if rule.rule_id == candidate.rule_id), "")
            if phrase.split(" ", 1)[0].casefold() != anchor:
                continue
            score = min(65, max(20, candidate.score - 45) + min(len(shared), 3) * 2)
            evidence = (f"wordnet_release:{WORDNET_RELEASE}", f"input_verb:{verb}",
                        f"anchor_verb:{anchor}", *(f"shared_synset:{item}" for item in shared),
                        f"alias_rule:{candidate.rule_id}")
            proposal = Candidate(candidate.capability, candidate.arguments, score,
                                 f"wordnet_{anchor}_{candidate.rule_id}", evidence)
            key = (proposal.capability, tuple(sorted(proposal.arguments.items())))
            previous = best.get(key)
            if previous is None or (proposal.score, proposal.rule_id) > (previous.score, previous.rule_id):
                best[key] = proposal
    return tuple(sorted(best.values(), key=lambda c: (-c.score, c.capability, c.rule_id)))
