"""The denylist.

These source tables are the answer key. Loading any of them makes the battery an
open-book exam that proves nothing. The loader refuses to run if the export
directory contains a file whose name matches one of them.

This is checked before any adapter reads a single byte.
"""

import re
import unicodedata

# Source tables that must never be loaded. Match is on normalised name, so
# "Config / Thresholds.csv", "config_thresholds.csv" and "CONFIG-THRESHOLDS.CSV"
# all match the same entry.
DENIED_TABLES = [
    "conflict rules",
    "config thresholds",
    "trip type rules",
    "capacity tiers",
    "movement types",
    "day cap locks",
    "automation registry",
]

# Any file from the conflict checker or the dispatch board, whatever it is named.
# These match as substrings of the normalised name.
DENIED_SUBSTRINGS = [
    "conflict checker",
    "conflictchecker",
    "dispatch board",
    "dispatchboard",
    "board ui",
]

# Fields that carry answer-key content even though they live on an allowed table.
#
# This is an addition to the written denylist, made after inspecting the source.
# The acknowledgement fields hold the conflict checker's own rule labels, one per
# human override. The override history is legitimate operational evidence and p08
# needs it. The rule label attached to each override is the answer key.
#
# The loader resolves this by loading the overrides with their labels replaced by
# opaque ids. See extract/README.md, "The override log".
ANSWER_KEY_FIELDS = [
    "acknowledged conflicts",
    "conflict status",
    "hard conflict",
    "soft conflict",
    "conflict id",
    "conflict key",
    "conflict signature",
    "guide conflict id",
]


def normalise(name: str) -> str:
    """Lowercase, strip an extension, and reduce every run of punctuation to one space."""
    name = unicodedata.normalize("NFKD", name)
    name = re.sub(r"\.(csv|tsv|json|ndjson|parquet|xlsx)$", "", name, flags=re.I)
    name = re.sub(r"[^a-z0-9]+", " ", name.lower())
    return name.strip()


class DenylistViolation(Exception):
    """Raised when the export contains answer-key material. The run is invalid."""


def check_table(name: str) -> None:
    """Raise if this source table name is on the denylist."""
    norm = normalise(name)
    if norm in DENIED_TABLES:
        raise DenylistViolation(
            f"DENIED SOURCE TABLE: {name!r} normalises to {norm!r}, which is on the "
            f"denylist. This table is answer-key material. Remove it from the export "
            f"directory and load again. The run is invalid until you do."
        )
    for frag in DENIED_SUBSTRINGS:
        if frag in norm:
            raise DenylistViolation(
                f"DENIED SOURCE TABLE: {name!r} normalises to {norm!r}, which contains "
                f"{frag!r}. Files from the conflict checker and the dispatch board are "
                f"answer-key material. The run is invalid until it is removed."
            )


def check_export_dir(paths) -> None:
    """Check every file in the export directory. Reports all violations, not just the first."""
    violations = []
    for p in sorted(paths):
        try:
            check_table(p.name)
        except DenylistViolation as exc:
            violations.append(str(exc))
    if violations:
        raise DenylistViolation(
            "Export rejected. %d denylisted file(s) present:\n\n%s"
            % (len(violations), "\n\n".join(violations))
        )


def is_answer_key_field(name: str) -> bool:
    return normalise(name) in ANSWER_KEY_FIELDS
