# Production-development entry point

This extracted suite is now organized for controlled production development.
The original export remains the immutable evidence baseline; files under
`production/` are generated development controls and do not alter the authority
of any packaged contract.

Start here:

1. Read `production/README.md` for the control model and commands.
2. Read `production/PRODUCTION_PLAN.md` for the ordered gates.
3. Review accepted decisions and remaining boundaries in `production/DECISION_LOG.md`.
4. Review the generic successor in `development/nlp-offline-interpreter/`.
5. Run `python production/validate_plan.py`.
6. Run `python production/run_checks.py --suite hardening` for the bounded
   engine, adapter, fuzzy, torture, and test-rig checks.
7. Run `python production/run_checks.py --suite baseline` from an environment
   containing the dependencies in `requirements-development.txt`.

The successor's generic core builds as a dependency-free wheel. Its staged
adapter to this historical suite is deliberately separate and requires the
baseline Lexicon Core and Natural Language source trees on `PYTHONPATH`.

The accepted bounded plan authorizes work through P09 only. No check result,
score, or generated artifact grants execution, mutation, receiving-system,
deployment, or production-ready authority.
