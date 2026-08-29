"""p03. Exclusivity and turnaround.

Two outputs.

First, every case of one resource assigned to overlapping work windows. If a kind
of resource never overlaps across a large number of assignments, that is a candidate
exclusivity rule. If it overlaps sometimes, the exceptions are the interesting part.

Second, and this is the valuable half, a histogram of gaps between consecutive
assignments per resource kind. The left edge where gaps essentially stop occurring
is a candidate turnaround minimum. No threshold is assumed, it is read from the
distribution.

No branching on any specific value of kind or role.
"""

from __future__ import annotations

from .base import candidate, left_edge, slug

PROBE = "p03"

GAP_BIN_MINUTES = 5
GAP_TAIL_FRACTION = 0.01     # what counts as "essentially stops occurring"
OVERLAP_SAMPLE = 10          # example rows carried as evidence


def _kind_volumes(con, min_assignments):
    """Resource kinds, with the resources that clear the assignment floor."""
    return con.execute("""
        WITH per_resource AS (
          SELECT r.kind, a.resource_id, count(*) AS n
          FROM assignments a
          JOIN resources r ON r.resource_id = a.resource_id
          WHERE a.start_ts IS NOT NULL AND a.end_ts IS NOT NULL
          GROUP BY 1, 2
        )
        SELECT kind,
               count(*) FILTER (WHERE n >= ?)          AS resources_over_floor,
               count(*)                                AS resources_total,
               sum(n) FILTER (WHERE n >= ?)            AS assignments_over_floor
        FROM per_resource
        WHERE kind IS NOT NULL
        GROUP BY 1
        ORDER BY 1
    """, [min_assignments, min_assignments]).fetchall()


def _overlaps(con, min_assignments):
    """One resource in two work windows at once."""
    return con.execute("""
        WITH eligible AS (
          SELECT a.resource_id
          FROM assignments a
          WHERE a.start_ts IS NOT NULL AND a.end_ts IS NOT NULL
          GROUP BY 1 HAVING count(*) >= ?
        )
        SELECT r.kind, a.resource_id, a.work_id, b.work_id,
               a.start_ts, a.end_ts, b.start_ts, b.end_ts
        FROM assignments a
        JOIN assignments b
          ON a.resource_id = b.resource_id
         AND a.assignment_id < b.assignment_id
         AND a.work_id <> b.work_id
         AND a.start_ts < b.end_ts
         AND b.start_ts < a.end_ts
        JOIN resources r ON r.resource_id = a.resource_id
        JOIN eligible e ON e.resource_id = a.resource_id
        WHERE a.start_ts IS NOT NULL AND a.end_ts IS NOT NULL
          AND b.start_ts IS NOT NULL AND b.end_ts IS NOT NULL
        ORDER BY r.kind, a.resource_id, a.start_ts, b.start_ts, a.work_id, b.work_id
    """, [min_assignments]).fetchall()


def _gaps(con, min_assignments):
    """Minutes between one assignment ending and the same resource's next starting."""
    return con.execute("""
        WITH eligible AS (
          SELECT resource_id FROM assignments
          WHERE start_ts IS NOT NULL AND end_ts IS NOT NULL
          GROUP BY 1 HAVING count(*) >= ?
        ),
        ordered AS (
          SELECT r.kind, a.resource_id, a.start_ts, a.end_ts,
                 lead(a.start_ts) OVER (PARTITION BY a.resource_id ORDER BY a.start_ts,
                                        a.assignment_id) AS next_start
          FROM assignments a
          JOIN resources r ON r.resource_id = a.resource_id
          JOIN eligible e ON e.resource_id = a.resource_id
          WHERE a.start_ts IS NOT NULL AND a.end_ts IS NOT NULL
        )
        SELECT kind, resource_id,
               date_diff('minute', end_ts, next_start) AS gap_minutes
        FROM ordered
        WHERE next_start IS NOT NULL
          AND date_diff('minute', end_ts, next_start) >= 0
        ORDER BY kind, resource_id, gap_minutes
    """, [min_assignments]).fetchall()


def run(con, guards):
    min_assignments = guards["min_assignments_per_resource"]
    min_observations = guards["min_observations"]
    out = []

    volumes = {kind: dict(zip(
        ("resources_over_floor", "resources_total", "assignments_over_floor"), rest))
        for kind, *rest in _kind_volumes(con, min_assignments)}

    # ---- exclusivity -------------------------------------------------
    overlaps_by_kind = {}
    for kind, resource_id, work_a, work_b, a_start, a_end, b_start, b_end in \
            _overlaps(con, min_assignments):
        overlaps_by_kind.setdefault(kind, []).append(
            {"resource_id": resource_id, "work_id_a": work_a, "work_id_b": work_b,
             "a_start": a_start, "a_end": a_end, "b_start": b_start, "b_end": b_end})

    for kind in sorted(volumes):
        vol = volumes[kind]
        assignments = vol["assignments_over_floor"] or 0
        if vol["resources_over_floor"] == 0 or assignments < min_observations:
            continue
        found = overlaps_by_kind.get(kind, [])
        resources_involved = len({row["resource_id"] for row in found})
        if found:
            statement = (
                f"A {kind} is sometimes booked on two jobs whose times overlap. "
                f"This happened {len(found)} times across {resources_involved} of them. "
                f"Is the overlap allowed, or are these mistakes?")
        else:
            statement = (
                f"A {kind} is never booked on two jobs whose times overlap. "
                f"Across {assignments} assignments there is not one exception. "
                f"Is that a rule?")
        out.append(candidate(
            PROBE, slug("exclusivity", kind), "exclusivity", statement,
            {"overlapping_pairs": len(found),
             "resources_with_an_overlap": resources_involved,
             "examples": found[:OVERLAP_SAMPLE]},
            {"kind": kind,
             "assignments_considered": assignments,
             "resources_over_assignment_floor": vol["resources_over_floor"],
             "resources_of_this_kind": vol["resources_total"],
             "min_assignments_per_resource": min_assignments}))

    # ---- turnaround --------------------------------------------------
    gaps_by_kind, gap_resources = {}, {}
    for kind, resource_id, gap in _gaps(con, min_assignments):
        gaps_by_kind.setdefault(kind, []).append(int(gap))
        gap_resources.setdefault(kind, set()).add(resource_id)

    for kind in sorted(gaps_by_kind):
        gaps = gaps_by_kind[kind]
        if len(gaps) < min_observations:
            continue
        edge, hard_floor, bins = left_edge(gaps, GAP_BIN_MINUTES, GAP_TAIL_FRACTION)
        if edge is None or edge <= 0:
            # The distribution starts at zero. Back to back work is normal for this
            # kind, so there is no turnaround floor to propose.
            continue
        below = sum(count for left, count in bins if left < edge)
        if hard_floor:
            statement = (
                f"After a {kind} finishes a job, at least {edge} minutes always passes "
                f"before it starts the next one. Across {len(gaps)} consecutive pairs "
                f"there is not one exception. Is {edge} minutes a required turnaround?")
        else:
            statement = (
                f"After a {kind} finishes a job, at least {edge} minutes almost always "
                f"passes before it starts the next one: {len(gaps) - below} of "
                f"{len(gaps)} consecutive pairs. The {below} exception(s) go as low as "
                f"{min(gaps)} minutes. Is {edge} minutes a required turnaround that got "
                f"broken those times, or is there no minimum?")
        out.append(candidate(
            PROBE, slug("turnaround", kind), "turnaround", statement,
            {"proposed_minimum_minutes": edge,
             "floor": "hard" if hard_floor else "soft",
             "gaps_below_the_edge": below,
             "bin_minutes": GAP_BIN_MINUTES,
             "tail_fraction": GAP_TAIL_FRACTION,
             "histogram_head": bins[:24],
             "observed_min_gap": min(gaps),
             "observed_median_gap": sorted(gaps)[len(gaps) // 2]},
            {"kind": kind,
             "consecutive_pairs": len(gaps),
             "resources_contributing": len(gap_resources[kind]),
             "min_assignments_per_resource": min_assignments}))

    return out
