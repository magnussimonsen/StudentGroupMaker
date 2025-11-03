"""
Quality metrics for evaluating group schedules.

This module calculates how well a schedule minimizes repeated pairings.
"""
from __future__ import annotations


def schedule_quality(rounds: list[list[list[str]]]) -> tuple[float, list[float], dict]:
    """
    Calculate quality metrics for a group schedule.
    
    Quality is measured by the percentage of new (never-before-seen) pairs
    in each round and overall.
    
    Args:
        rounds: List of rounds, where each round is a list of groups
        
    Returns:
        Tuple of:
        - overall_pct: Overall percentage of new pairs
        - per_round_pct: List of percentages for each round
        - counts: Detailed count information
    """
    seen_pairs = set()
    total_pairs = 0
    new_pairs = 0
    per_round_pct = []
    per_round_counts = []

    for groups in rounds:
        r_total = 0
        r_new = 0
        
        for g in groups:
            for i in range(len(g)):
                for j in range(i + 1, len(g)):
                    a, b = g[i], g[j]
                    pair = tuple(sorted((a, b)))
                    total_pairs += 1
                    r_total += 1
                    
                    if pair not in seen_pairs:
                        seen_pairs.add(pair)
                        new_pairs += 1
                        r_new += 1
        
        r_pct = 100.0 * r_new / r_total if r_total else 100.0
        per_round_pct.append(r_pct)
        per_round_counts.append({"new": r_new, "total": r_total})

    overall_pct = 100.0 * new_pairs / total_pairs if total_pairs else 100.0
    counts = {
        "overall": {"new": new_pairs, "total": total_pairs},
        "per_round": per_round_counts,
    }
    
    return overall_pct, per_round_pct, counts
