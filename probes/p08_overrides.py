"""p08. Overrides.

From changes: what field gets changed after being set, how often, by whom, and how
many days before the work date. Ranked by frequency.

Every repeated override is a candidate rule the current system has wrong. Either the
system is flagging something that is fine, or it is not flagging something that is
not, and a human has been closing the gap by hand all season.

Note on labels. When the override log comes from an acknowledgement field, the field
name here is an opaque id, not the rule name, because the rule name is answer-key
content. See extract/README.md. Frequency, actor spread and lead time survive that
substitution, which is what this probe ranks on.
"""

from __future__ import annotations

from .base import candidate, slug

PROBE = "p08"

DEFAULT_MIN_EVENTS = 3   # below this a field is a one-off, not a pattern


def run(con, guards):
    min_events = guards.get("min_change_events") or DEFAULT_MIN_EVENTS
    total = con.execute("SELECT count(*) FROM changes").fetchone()[0]
    if not total:
        return []

    rows = con.execute("""
        SELECT c.entity_table,
               c.field,
               count(*)                              AS events,
               count(DISTINCT c.entity_id)           AS entities,
               count(DISTINCT c.changed_by)          AS actors,
               min(c.changed_at)                     AS first_seen,
               max(c.changed_at)                     AS last_seen
        FROM changes c
        WHERE c.field IS NOT NULL
          AND c.old_value IS NOT NULL          -- changed after being set
        GROUP BY 1, 2
        HAVING count(*) >= ?
        ORDER BY count(*) DESC, c.entity_table, c.field
    """, [min_events]).fetchall()

    # Lead time: days between the override and the work it was made against.
    leads = {}
    for table, field, days in con.execute("""
        SELECT c.entity_table, c.field,
               date_diff('day', c.changed_at, w.start_ts) AS lead_days
        FROM changes c
        JOIN work w ON w.work_id = c.entity_id
        WHERE c.entity_table = 'work'
          AND c.changed_at IS NOT NULL AND w.start_ts IS NOT NULL
        ORDER BY 1, 2, 3
    """).fetchall():
        leads.setdefault((table, field), []).append(int(days))

    actors_by_field = {}
    for table, field, who, n in con.execute("""
        SELECT entity_table, field, coalesce(changed_by, '(unrecorded)'), count(*)
        FROM changes WHERE field IS NOT NULL AND old_value IS NOT NULL
        GROUP BY 1, 2, 3 ORDER BY 1, 2, 4 DESC, 3
    """).fetchall():
        actors_by_field.setdefault((table, field), []).append({"changed_by": who, "events": n})

    out = []
    for rank, (table, field, events, entities, actors, first_seen, last_seen) in \
            enumerate(rows, start=1):
        lead = sorted(leads.get((table, field), []))
        lead_summary = None
        if lead:
            lead_summary = {
                "n": len(lead),
                "min_days": lead[0],
                "median_days": lead[len(lead) // 2],
                "max_days": lead[-1],
                "same_day_or_later": sum(1 for d in lead if d <= 0),
            }

        when = ""
        if lead_summary:
            when = (f" Typically {lead_summary['median_days']} day(s) before the job, "
                    f"and {lead_summary['same_day_or_later']} of them on the day or after.")

        statement = (
            f"Somebody went back and changed {field} on {entities} {table} records, "
            f"{events} times in all, after it had already been set.{when} "
            f"What is the system getting wrong that keeps needing this?")

        out.append(candidate(
            PROBE, slug("override", table, field), "any", statement,
            {"entity_table": table,
             "field": field,
             "rank_by_frequency": rank,
             "events": events,
             "distinct_entities": entities,
             "distinct_actors": actors,
             "actors": actors_by_field.get((table, field), []),
             "first_seen": first_seen,
             "last_seen": last_seen,
             "lead_time_days": lead_summary},
            {"change_rows_total": total,
             "events_for_this_field": events,
             "min_events_per_field": min_events,
             "share_of_all_overrides": round(events / total, 4)}))
    return out
