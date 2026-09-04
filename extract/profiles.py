"""Export profiles.

The full export is far more structured than a typical target business will ever be.
Two years of schema work went into it: typed links, populated config, named tables. A
normal client has booking transaction history, maybe an assignment record, message
threads, and some SOPs in a document nobody reads.

So the battery runs twice on the same probes, and the delta is the finding.

The lean profile keeps only what a typical operation would plausibly produce. The
principle for the cut: drop anything that exists because the operator built it rather
than because the operation produced it.

The six table schema never changes between profiles. A dropped column is present and
null, a dropped table is present and empty. That is the honest model of a leaner
client: they have the concept, they just have no data in it. It also means p05, which
measures fill rates, sees the thinning rather than being blinded to it.
"""

from __future__ import annotations

PROFILES = {
    "full": {
        "label": "full",
        "description": "Everything the export carries. The operator's own instrumented base.",
        "skip_source_tables": [],
        "drop_tables": [],
        "drop_columns": {},
        "collapse_resource_kind": False,
        "rationale": [],
    },
    "lean": {
        "label": "lean",
        "description": (
            "What a typical operation would plausibly produce: transaction records for "
            "work, assignment records with times, and locations."),

        # Source tables the adapter does not read at all.
        "skip_source_tables": ["Movements", "Rig Assignments"],

        # Landing tables that stay in the schema but receive no rows.
        "drop_tables": ["location_travel", "changes"],

        # Landing columns that stay in the schema but are set null.
        "drop_columns": {
            "work": ["location_id"],
            "resources": ["home_location_id"],
        },

        # Use each resource spec's literal kind instead of a maintained type column.
        "collapse_resource_kind": True,

        "rationale": [
            "Movements: a client has bookings. Almost none has a structured record of "
            "every vehicle repositioning. That lives on a whiteboard or in a text "
            "thread. Dropping it also removes the only source of location_id.",
            "Rig Assignments: having two overlapping assignment sources is itself the "
            "artifact. The links on the booking are the more typical shape.",
            "location_travel: a measured travel matrix between locations is pure build. "
            "No probe reads it today, so this costs nothing now.",
            "changes: the override log. No small business keeps a structured record of "
            "a human clearing a flag. This is the largest and most defensible cut.",
            "work.location_id: in this export it comes only from a typed link on a "
            "table the operator built.",
            "resources.home_location_id: a maintained home base per resource is build.",
            "resource kind: a vehicle list exists anywhere. A maintained van and "
            "trailer taxonomy on top of it does not.",
        ],
    },
}


def get(name):
    if name not in PROFILES:
        raise SystemExit(f"No profile named {name!r}. Known profiles: {sorted(PROFILES)}")
    return PROFILES[name]
