"""
Visualization functions for group schedules.

This module provides functions to visualize co-occurrence patterns
in group schedules.
"""
from __future__ import annotations
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from matplotlib.colors import BoundaryNorm
matplotlib.use('Qt5Agg')  # Use Qt backend for PySide6 integration


def build_pair_matrix(rounds: list[list[list[str]]]) -> tuple[list[str], list[list[int]]]:
    """
    Build a co-occurrence matrix showing how many times each pair of students
    was in the same group across all rounds.
    
    Args:
        rounds: List of rounds, where each round is a list of groups
        
    Returns:
        Tuple of (student_names, matrix) where matrix[i][j] is the number of
        times student i and student j were in the same group
    """
    # Get sorted list of all unique student names
    names = sorted({name for round_ in rounds for group in round_ for name in group})
    index = {name: i for i, name in enumerate(names)}
    n = len(names)
    
    # Initialize matrix with zeros
    matrix = [[0] * n for _ in range(n)]
    
    # Count co-occurrences
    for groups in rounds:
        for group in groups:
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    a, b = index[group[i]], index[group[j]]
                    matrix[a][b] += 1
                    matrix[b][a] += 1
    
    return names, matrix


def create_heatmap_figure(names: list[str], matrix: list[list[int]]):
    """
    Create a matplotlib figure with a heatmap of the co-occurrence matrix.
    
    Args:
        names: List of student names
        matrix: Co-occurrence matrix
        
    Returns:
        matplotlib Figure object
    """
    n = len(names)
    
    # Create figure. Use constrained_layout so axis labels and colorbar are included in PNG exports.
    # Fall back to tight_layout if constrained layout isn't supported.
    fig = None
    ax = None
    try:
        fig, ax = plt.subplots(
            figsize=(max(8, n * 0.5), max(8, n * 0.5)),
            constrained_layout=True,
        )
    except TypeError:
        # Older Matplotlib: no constrained_layout; create normally and adjust later
        fig, ax = plt.subplots(figsize=(max(8, n * 0.5), max(8, n * 0.5)))
    
    # Create heatmap with discrete integer bins and integer-only colorbar ticks
    cmap = plt.get_cmap('YlOrRd')
    max_count = 0
    if matrix and matrix[0]:
        max_count = max(max(row) for row in matrix)

    # Define boundaries centered on integers (… -0.5, 0.5, 1.5, …) so each integer maps to a color band
    if max_count > 0:
        boundaries = np.arange(-0.5, max_count + 1.5, 1)
        ticks = np.arange(0, max_count + 1, 1)
    else:
        # All zeros; create a single band around 0
        boundaries = np.array([-0.5, 0.5])
        ticks = [0]
    norm = BoundaryNorm(boundaries, ncolors=cmap.N, clip=True)

    im = ax.imshow(matrix, cmap=cmap, norm=norm, interpolation='nearest')
    
    # Set ticks and labels
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(names, rotation=90, ha='right')
    ax.set_yticklabels(names)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, ticks=ticks)
    cbar.set_label('Times in same group', rotation=270, labelpad=20)
    
    # Add text annotations
    # for i in range(n):
    #    for j in range(n):
    #        if i != j:  # Don't show diagonal
    #            text = ax.text(j, i, str(matrix[i][j]),
    #                         ha="center", va="center", color="black" if matrix[i][j] < 3 else "white",
    #                         fontsize=8)

    ax.set_title("How many times each pair was in the same group")
    # If constrained_layout wasn't available, do a best-effort layout adjustment
    if not getattr(fig, 'get_constrained_layout_pads', None):
        # Leave a bit more room for long, rotated x-labels and the colorbar
        try:
            fig.tight_layout()
        except Exception:
            pass
    
    return fig

