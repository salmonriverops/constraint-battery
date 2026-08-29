"""Shared probe machinery.

A probe emits candidates. It never asserts that a rule exists. That word is
reserved for something a human confirmed.

Every candidate carries:
  probe             the probe id
  candidate_id      stable across reruns on the same input
  proposed_type     exclusivity, turnaround, capacity, dependency, exemption, ...
  statement         one plain sentence a non-technical person could confirm or deny
  evidence          the counts or rows behind it
  confidence_inputs the volumes that make it worth believing
"""

from __future__ import annotations

import hashlib
import re


def slug(*parts) -> str:
    """A readable, stable fragment for a candidate id."""
    text = "_".join(str(p) for p in parts if p not in (None, ""))
    text = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()
    if len(text) > 48:
        text = text[:40] + "-" + hashlib.sha256(text.encode()).hexdigest()[:7]
    return text or "unnamed"


def candidate(probe, cid, proposed_type, statement, evidence, confidence_inputs):
    return {
        "probe": probe,
        "candidate_id": f"{probe}-{cid}",
        "proposed_type": proposed_type,
        "statement": statement,
        "evidence": evidence,
        "confidence_inputs": confidence_inputs,
    }


def histogram(values, bin_size):
    """Bin a list of numbers. Returns [(left_edge, count)] with every bin present."""
    if not values:
        return []
    top = max(values)
    counts = {}
    for value in values:
        counts[int(value // bin_size) * bin_size] = counts.get(
            int(value // bin_size) * bin_size, 0) + 1
    return [(edge, counts.get(edge, 0))
            for edge in range(0, int(top // bin_size) * bin_size + bin_size, bin_size)]


def left_edge(values, bin_size, tail_fraction):
    """Find where the distribution effectively starts.

    Returns the lowest bin edge L such that everything below L accounts for no more
    than tail_fraction of all observations. No threshold is assumed. L is read off
    the distribution.

    Also returns whether the region below L is completely empty. An empty region is
    a hard floor. A sparsely populated one is a soft floor, which is weaker evidence.
    """
    bins = histogram(values, bin_size)
    total = len(values)
    if not bins or total == 0:
        return None, None, bins
    budget = total * tail_fraction
    running = 0
    edge = 0
    for left, count in bins:
        if running + count > budget:
            edge = left
            break
        running += count
        edge = left + bin_size
    below = sum(count for left, count in bins if left < edge)
    return edge, below == 0, bins


def right_edge_shape(counts_by_value, cliff_ratio):
    """Classify the right edge of an integer distribution as a cliff or a taper.

    A tapering tail is a business limit: the top values are rare and fade out.
    A cliff is a rule: mass piles up at the maximum and then stops dead.

    The test is the share of observations sitting exactly at the maximum, relative
    to the busiest value. Nothing about the domain is assumed.
    """
    if not counts_by_value:
        return None
    values = sorted(counts_by_value)
    top = values[-1]
    total = sum(counts_by_value.values())
    peak = max(counts_by_value.values())
    at_top = counts_by_value[top]
    below = counts_by_value.get(top - 1, 0)
    return {
        "observed_max": top,
        "observations": total,
        "count_at_max": at_top,
        "count_below_max": below,
        "share_at_max": round(at_top / total, 4),
        "max_over_peak": round(at_top / peak, 4),
        "shape": "cliff" if at_top / peak >= cliff_ratio else "taper",
    }
