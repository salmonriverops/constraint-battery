# What differs from the private original

Four personal names in four judging notes were replaced with roles: the owner,
a guide, a part time guide. Two of those notes concern a specific person's
credential record being out of date, which is not something to publish about an
employee.

The replacement was applied across the whole history rather than as a final
commit, so the names are not recoverable from this repository.

Nothing else changed. No verdict, no key row, no candidate, no probe, no
threshold. `score.md` and `delta.md` were regenerated after the redaction and
every number is identical, which is checkable by running:

    python3 cli.py score runs/2026-09-04-crewfix-full

The answer key contains no names. Five were removed from K063 on 2026-09-04,
before the key was frozen, and that is recorded in `key/provenance.json`.

The private original retains the names and remains the canonical record. Ask
and I will walk you through it.
