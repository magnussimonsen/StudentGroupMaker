"""
Visualization functions for group schedules.

This module provides functions to visualize co-occurrence patterns
in group schedules.
"""
from __future__ import annotations
import matplotlib.pyplot as plt
import matplotlib
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
    
    # Create figure
    fig, ax = plt.subplots(figsize=(max(8, n * 0.5), max(8, n * 0.5)))
    
    # Create heatmap
    im = ax.imshow(matrix, cmap='YlOrRd', interpolation='nearest')
    
    # Set ticks and labels
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(names, rotation=90, ha='right')
    ax.set_yticklabels(names)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Times in same group', rotation=270, labelpad=20)
    
    # Add text annotations
    for i in range(n):
        for j in range(n):
            if i != j:  # Don't show diagonal
                text = ax.text(j, i, str(matrix[i][j]),
                             ha="center", va="center", color="black" if matrix[i][j] < 3 else "white",
                             fontsize=8)
    
    ax.set_title("Student Co-occurrence Matrix\n(How many times each pair was in the same group)")
    fig.tight_layout()
    
    return fig

