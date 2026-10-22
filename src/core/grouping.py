"""
Core grouping algorithms for generating balanced student groups.

This module contains the core logic for creating student groups with
minimal repetition of student pairs across multiple rounds.
"""
from __future__ import annotations
import random
from collections import defaultdict


def partition_sizes(n_students: int, n_groups: int) -> list[int]:
    """
    Calculate balanced group sizes.
    
    Args:
        n_students: Total number of students
        n_groups: Number of groups to create
        
    Returns:
        List of group sizes (some may be larger by 1 to distribute remainders)
    """
    base = n_students // n_groups
    rem = n_students % n_groups
    return [base + 1] * rem + [base] * (n_groups - rem)


def round_cost(groups: list[list[str]], together: dict[str, dict[str, int]]) -> int:
    """
    Calculate the cost of a round based on pair repetitions.

    Args:
        groups: List of groups, where each group is a list of student names
        together: together[a][b] is how many times a and b have been in a group

    Returns:
        Total cost (higher means more repetitions)
    """
    cost = 0
    for g in groups:
        for i in range(len(g)):
            for j in range(i + 1, len(g)):
                cost += together[g[i]][g[j]]
    return cost


def build_round(
    students: list[str],
    n_groups: int,
    pair_counts: dict,
    restarts: int = 200,
    rng: random.Random | None = None
) -> tuple[list[list[str]], int]:
    """
    Build a single round of groups with minimal pair repetition.
    
    Uses a greedy algorithm with random restarts to minimize the number
    of repeated student pairs.
    
    Args:
        students: List of student names
        n_groups: Number of groups to create
        pair_counts: Dictionary tracking pair history
        restarts: Number of random restarts to try
        rng: Random number generator (creates new if None)
        
    Returns:
        Tuple of (best groups found, cost of best solution)
    """
    if rng is None:
        rng = random.Random()
        
    # Clamp groups to number of students to avoid zero-sized groups
    n_groups = max(1, min(n_groups, len(students)))
    sizes = partition_sizes(len(students), n_groups)
    best_groups, best_cost = None, float("inf")

    # Pair history as a plain lookup table, built once per round, since building
    # a frozenset for every lookup in the loops below made generation slow
    together = {
        s: {t: pair_counts.get(frozenset((s, t)), 0) for t in students}
        for s in students
    }
    # Degree (number of previous pairings) of each student; the same for every restart
    deg = {
        s: sum(count for t, count in together[s].items() if t != s)
        for s in students
    }

    for _ in range(restarts):
        unassigned = students[:]
        rng.shuffle(unassigned)
        groups = []

        # Sort by degree (high to low) to prioritize students with many pairings
        unassigned.sort(key=lambda s: (-deg[s], rng.random()))

        # Build groups greedily
        for size in sizes:
            # Skip zero-sized groups (can occur if requested groups > students)
            if size <= 0:
                continue
            # Safety: if unassigned is empty, stop building
            if not unassigned:
                break
            seed = unassigned.pop(0)
            group = [seed]
            
            for _ in range(size - 1):
                best_cand, best_incr = None, float("inf")
                
                # Sample pool to speed up for large classes
                pool = unassigned if len(unassigned) <= 20 else rng.sample(unassigned, 20)
                
                for cand in pool:
                    past = together[cand]
                    incr = sum(past[x] for x in group)
                    if incr < best_incr or (incr == best_incr and rng.random() < 0.5):
                        best_cand, best_incr = cand, incr
                
                if best_cand is None:
                    best_cand = unassigned[0]
                    
                group.append(best_cand)
                unassigned.remove(best_cand)
                
            groups.append(group)

        cost = round_cost(groups, together)
        if cost < best_cost:
            best_groups, best_cost = groups, cost
            if best_cost == 0:
                break

    return best_groups, best_cost


def schedule_groups(
    students: list[str],
    n_groups: int,
    rounds: int,
    seed: int | None = None,
    restarts: int = 200
) -> list[list[list[str]]]:
    """
    Generate a complete schedule of groups across multiple rounds.
    
    Args:
        students: List of student names
        n_groups: Number of groups per round
        rounds: Number of rounds to generate
        seed: Random seed for reproducibility (None for random)
        restarts: Number of random restarts per round
        
    Returns:
        List of rounds, where each round is a list of groups
    """
    rng = random.Random(seed)
    students = students[:]
    pair_counts = defaultdict(int)
    all_rounds = []

    for _ in range(rounds):
        # Clamp n_groups per round to current number of students to avoid zero-size groups
        effective_groups = max(1, min(n_groups, len(students)))
        groups, _ = build_round(students, effective_groups, pair_counts, restarts=restarts, rng=rng)
        all_rounds.append(groups)
        
        # Update pair counts
        for g in groups:
            for i in range(len(g)):
                for j in range(i + 1, len(g)):
                    pair_counts[frozenset((g[i], g[j]))] += 1
        
        # Shuffle for next round
        rng.shuffle(students)

    return all_rounds
