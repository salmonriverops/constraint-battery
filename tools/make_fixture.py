"""Generate a deterministic synthetic export for testing the battery.

This is not business data. Every name and id is invented. It exists so the loader
and the probes can be exercised without an export on disk, and so the planted
structure gives the probes something known to find.

Planted structure, for checking probe behaviour:
  - people never take a second job inside 45 minutes of finishing one
  - customer_count piles up at 18 and stops dead (a cliff)
  - no resource works more than 2 jobs in a day
  - work_type 'shuttle' never carries a customer count, 'trip' always does
  - two override labels repeat often, the rest are one-offs
"""

from __future__ import annotations

import json
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

SEED = 20260829
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "data/fixture_export")

TURNAROUND_MIN = 45
CUSTOMER_CEILING = 18
JOBS_PER_RESOURCE_PER_DAY = 2


def rid(prefix, n):
    return f"rec{prefix}{n:012d}"


def main():
    rng = random.Random(SEED)
    OUT.mkdir(parents=True, exist_ok=True)

    locations = [{"id": rid("L", i), "Name": f"Location {i}"} for i in range(1, 7)]
    people = [{"id": rid("G", i), "Name": f"Person {i}", "Location base": f"Location {1 + i % 6}"}
              for i in range(1, 25)]
    vehicles = [{"id": rid("V", i), "Unit name": f"Unit {i}",
                 "Type": "Van" if i % 3 else "Trailer",
                 "Location base": f"Location {1 + i % 6}"} for i in range(1, 13)]

    ops, movements, rigs, changes_by_op = [], [], [], {}
    day = datetime(2026, 6, 1, 7, 0)
    busy = {p["id"]: [] for p in people}
    op_n = mv_n = 0

    for offset in range(90):
        date = day + timedelta(days=offset)
        per_day = {p["id"]: 0 for p in people}
        for slot in range(rng.randint(3, 7)):
            op_n += 1
            work_type = "trip" if slot % 3 else "shuttle"
            start = date.replace(hour=8) + timedelta(minutes=90 * slot)
            end = start + timedelta(minutes=rng.choice([180, 240, 300]))
            # 'shuttle' never carries a customer count, 'trip' always does.
            if work_type == "trip":
                count = min(CUSTOMER_CEILING, int(abs(rng.gauss(12, 4))) + 4)
                if rng.random() < 0.30:
                    count = CUSTOMER_CEILING
            else:
                count = None
            op = {
                "id": rid("O", op_n),
                "Date": date.date().isoformat(),
                "Trip type": work_type,
                "Trip start": start.isoformat(timespec="seconds") + "Z",
                "Trip end": end.isoformat(timespec="seconds") + "Z",
                "Status": rng.choice(["Confirmed", "Confirmed", "Confirmed", "Cancelled"]),
                "Guest count": count,
                "Guide Availability": [],
                "Vehicle": [],
                "Trailer": [],
                "Acknowledged conflicts": "",
            }
            # Assign people who are free and respect the planted turnaround floor.
            candidates = [p for p in people if per_day[p["id"]] < JOBS_PER_RESOURCE_PER_DAY]
            rng.shuffle(candidates)
            picked = []
            for person in candidates:
                if len(picked) >= rng.randint(1, 3):
                    break
                clear = all(
                    start >= prev_end + timedelta(minutes=TURNAROUND_MIN) or
                    end + timedelta(minutes=TURNAROUND_MIN) <= prev_start
                    for prev_start, prev_end in busy[person["id"]])
                if clear:
                    picked.append(person)
                    busy[person["id"]].append((start, end))
                    per_day[person["id"]] += 1
            op["Guide Availability"] = [{"id": p["id"], "name": p["Name"]} for p in picked]
            vehicle = rng.choice(vehicles)
            op["Vehicle"] = [{"id": vehicle["id"], "name": vehicle["Unit name"]}]
            ops.append(op)

            if rng.random() < 0.25:
                label = rng.choice(["dbl-" + rid("G", rng.randint(1, 24)), "caps",
                                    "caps", "busconf", "busconf", "busconf",
                                    f"oneoff-{op_n}"])
                ack_day = (date - timedelta(days=rng.randint(0, 5))).date().isoformat()
                changes_by_op.setdefault(op["id"], []).append(
                    f"{label} :: manager :: {ack_day}")

        for _ in range(rng.randint(1, 4)):
            mv_n += 1
            start = date.replace(hour=6) + timedelta(minutes=45 * rng.randint(0, 14))
            movements.append({
                "id": rid("M", mv_n),
                "Date": date.date().isoformat(),
                "Start": start.isoformat(timespec="seconds") + "Z",
                "End": (start + timedelta(minutes=rng.choice([60, 90, 120]))).isoformat(
                    timespec="seconds") + "Z",
                "Movement Type": [{"id": rid("T", rng.randint(1, 4))}],
                "Origin": [{"id": rng.choice(locations)["id"]}],
                "Status": "Complete",
                "Passengers": rng.randint(0, 14),
                "Driver (link)": [{"id": rng.choice(people)["id"]}],
                "Vehicle": [{"id": rng.choice(vehicles)["id"]}],
                "Trailer": [],
                "Acknowledged conflicts": "",
            })

    for op in ops:
        op["Acknowledged conflicts"] = "\n".join(changes_by_op.get(op["id"], []))

    routes = [{"id": rid("R", i * 6 + j), "From": [{"id": a["id"]}], "To": [{"id": b["id"]}],
               "Drive minutes": 15 + (i * 7 + j * 11) % 90,
               "Sample count": (i + j) % 4}
              for i, a in enumerate(locations) for j, b in enumerate(locations) if a is not b]

    for name, rows in [("Daily Ops", ops), ("Movements", movements),
                       ("Guides & Staff", people), ("Vehicles", vehicles),
                       ("Locations", locations), ("Routes", routes),
                       ("Rig Assignments", rigs), ("Boats", [])]:
        (OUT / f"{name}.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")

    print(f"wrote {len(ops)} Daily Ops, {len(movements)} Movements, {len(people)} people, "
          f"{len(vehicles)} vehicles, {len(routes)} routes to {OUT}")


if __name__ == "__main__":
    main()
