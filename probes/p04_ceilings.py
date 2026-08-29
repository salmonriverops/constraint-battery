"""p04. Ceilings.

For each countable dimension, plot the distribution and look at the right edge.

A tapering tail is a business limit: big days are rare and fade out. A cliff is a
rule: the count piles up at one value and then stops dead. The probe reports the
observed max and the shape, and lets the human decide which it is.

The dimensions are structural. None of them branches on a value of kind or role.
"""

from __future__ import annotations

from .base import candidate, right_edge_shape, slug

PROBE = "p04"

CLIFF_RATIO = 0.5   # mass at the max, relative to the busiest value

DIMENSIONS = [
    ("customers_per_work",
     "guests on one job",
     """SELECT customer_count AS v, count(*) AS n
        FROM work WHERE customer_count IS NOT NULL GROUP BY 1"""),

    ("resources_per_work",
     "resources assigned to one job",
     """SELECT n AS v, count(*) AS n FROM (
          SELECT work_id, count(DISTINCT resource_id) AS n
          FROM assignments WHERE work_id IS NOT NULL GROUP BY 1) GROUP BY 1"""),

    ("work_per_day",
     "jobs on one day",
     """SELECT n AS v, count(*) AS n FROM (
          SELECT cast(start_ts AS DATE) AS d, count(*) AS n
          FROM work WHERE start_ts IS NOT NULL GROUP BY 1) GROUP BY 1"""),

    ("work_per_resource_per_day",
     "jobs for one resource on one day",
     """SELECT n AS v, count(*) AS n FROM (
          SELECT a.resource_id, cast(a.start_ts AS DATE) AS d,
                 count(DISTINCT a.work_id) AS n
          FROM assignments a WHERE a.start_ts IS NOT NULL GROUP BY 1, 2) GROUP BY 1"""),

    ("work_per_location_per_day",
     "jobs at one location on one day",
     """SELECT n AS v, count(*) AS n FROM (
          SELECT location_id, cast(start_ts AS DATE) AS d, count(*) AS n
          FROM work WHERE start_ts IS NOT NULL AND location_id IS NOT NULL
          GROUP BY 1, 2) GROUP BY 1"""),
]


def run(con, guards):
    min_observations = guards["min_observations"]
    out = []

    for name, phrase, sql in DIMENSIONS:
        rows = con.execute(sql).fetchall()
        counts = {int(value): int(n) for value, n in rows if value is not None}
        if not counts or sum(counts.values()) < min_observations:
            continue
        shape = right_edge_shape(counts, CLIFF_RATIO)
        top = shape["observed_max"]

        if shape["shape"] == "cliff":
            statement = (
                f"The number of {phrase} never goes above {top}. It reaches {top} "
                f"{shape['count_at_max']} times out of {shape['observations']} and never "
                f"once goes higher. Is {top} a limit somebody set?")
        else:
            statement = (
                f"The number of {phrase} tops out at {top}, but only "
                f"{shape['count_at_max']} times out of {shape['observations']}, and the "
                f"numbers just below it thin out gradually. Is {top} a limit, or just "
                f"the busiest it ever got?")

        distribution = [{"value": value, "count": counts[value]} for value in sorted(counts)]
        out.append(candidate(
            PROBE, slug("ceiling", name), "capacity", statement,
            {"dimension": name,
             "observed_max": top,
             "shape": shape["shape"],
             "count_at_max": shape["count_at_max"],
             "count_one_below_max": shape["count_below_max"],
             "share_at_max": shape["share_at_max"],
             "max_over_busiest_value": shape["max_over_peak"],
             "cliff_ratio_used": CLIFF_RATIO,
             "distribution": distribution},
            {"observations": shape["observations"],
             "distinct_values": len(counts),
             "min_observations": min_observations}))
    return out
