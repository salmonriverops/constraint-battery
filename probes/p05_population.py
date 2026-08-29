"""p05. Population.

Fill rate per field, partitioned by work_type, location and status.

A field that is always populated for one partition and never for another is not a
data quality problem. It is a rule wearing a disguise: either the field is required
in that case (a dependency), or that case is exempt from it (an exemption).

The probe reports both the rule shape and the partition.
"""

from __future__ import annotations

from .base import candidate, slug

PROBE = "p05"

HIGH = 0.95   # "near 100 percent"
LOW = 0.05    # "near 0 percent"

# Fields whose fill rate carries information. The partition columns themselves are
# excluded from the field list when they are the partition.
FIELDS = ["work_type", "start_ts", "end_ts", "location_id", "status", "customer_count"]
PARTITIONS = ["work_type", "location_id", "status"]


def run(con, guards):
    min_populated = guards["min_populated_rows_per_field"]
    min_partition_rows = guards["min_instances_per_work_type"]
    out = []

    total_rows = con.execute("SELECT count(*) FROM work").fetchone()[0]
    if not total_rows:
        return out

    populated = {
        field: con.execute(
            f"SELECT count(*) FROM work WHERE {field} IS NOT NULL").fetchone()[0]
        for field in FIELDS}

    for partition in PARTITIONS:
        for field in FIELDS:
            if field == partition:
                continue
            if populated[field] < min_populated:
                continue
            rows = con.execute(f"""
                SELECT coalesce(cast({partition} AS TEXT), '(blank)') AS part,
                       count(*) AS rows,
                       count({field}) AS filled
                FROM work
                GROUP BY 1
                HAVING count(*) >= {min_partition_rows}
                ORDER BY 1
            """).fetchall()
            if len(rows) < 2:
                continue

            rates = [(part, int(n), int(filled), filled / n) for part, n, filled in rows]
            high = [r for r in rates if r[3] >= HIGH]
            low = [r for r in rates if r[3] <= LOW]
            if not high or not low:
                continue

            # Report the sharpest pair, so the statement names one partition each side.
            top = max(high, key=lambda r: (r[3], r[1]))
            bottom = min(low, key=lambda r: (r[3], -r[1]))

            statement = (
                f"When {partition} is {top[0]!r}, {field} is filled in almost every time "
                f"({top[2]} of {top[1]}). When it is {bottom[0]!r}, it is almost never "
                f"filled in ({bottom[2]} of {bottom[1]}). Is {field} required for one and "
                f"not the other?")

            out.append(candidate(
                PROBE, slug("population", field, "by", partition),
                "dependency" if top[3] >= HIGH else "exemption",
                statement,
                {"field": field,
                 "partition": partition,
                 "required_in": {"value": top[0], "rows": top[1], "filled": top[2],
                                 "fill_rate": round(top[3], 4)},
                 "absent_in": {"value": bottom[0], "rows": bottom[1], "filled": bottom[2],
                               "fill_rate": round(bottom[3], 4)},
                 "all_partitions": [{"value": p, "rows": n, "filled": f,
                                     "fill_rate": round(rate, 4)}
                                    for p, n, f, rate in rates],
                 "high_threshold": HIGH, "low_threshold": LOW},
                {"rows_in_work": total_rows,
                 "rows_with_this_field_populated": populated[field],
                 "partitions_over_row_floor": len(rates),
                 "min_partition_rows": min_partition_rows,
                 "min_populated_rows_per_field": min_populated}))

            # One exemption candidate per pair, stated the other way round, because
            # the two readings lead to different questions for the human.
            out.append(candidate(
                PROBE, slug("exemption", field, "by", partition, bottom[0]),
                "exemption",
                f"{field} is essentially never filled in when {partition} is "
                f"{bottom[0]!r} ({bottom[2]} of {bottom[1]}), though it is filled in "
                f"elsewhere. Is that case exempt from needing {field}?",
                {"field": field, "partition": partition, "partition_value": bottom[0],
                 "rows": bottom[1], "filled": bottom[2],
                 "fill_rate": round(bottom[3], 4)},
                {"rows_in_work": total_rows,
                 "rows_with_this_field_populated": populated[field],
                 "rows_in_this_partition": bottom[1],
                 "min_partition_rows": min_partition_rows}))
    return out
