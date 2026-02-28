"""
Visualization module
Contains classes and functions for visualizing MCDA results
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.colors as mcolors
from PyQt5.QtWidgets import QMessageBox
from typing import List, Optional


class PlotCanvas(FigureCanvas):
    """
    Canvas for plotting 3D visualization of MCDA results
    """
    
    def __init__(self, parent=None):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        super(PlotCanvas, self).__init__(self.fig)
        self.setParent(parent)
        self.plot([])
        
    def plot(self, data, criterion_index=0, green_indices=None):
        """
        Plot 3D visualization of data
        
        Args:
            data: Data matrix to visualize
            criterion_index: Index of the criterion to use as X-axis
            green_indices: Indices of points to highlight in green
        """
        self.ax.clear()
        if len(data) == 0:
            return
            
        data = np.array(data)
        X = data[:, criterion_index]
        Y = np.prod(np.delete(data, criterion_index, axis=1), axis=1)
        Z = np.prod(data, axis=1)
        
        total_points = len(data)
        if green_indices is None:
            green_indices = []

        colors = [self._get_color_gradient(i, total_points) for i in range(total_points)]
        for idx in green_indices:
            if idx == green_indices[0]:
                colors[idx] = (0, 1, 0)  # Green color for specified indices

        # Convert colors to RGBA format for use in scatter
        rgba_colors = np.zeros((len(colors), 4))
        for i, color in enumerate(colors):
            rgba_colors[i, :] = (*color, 1)  # Add alpha channel equal to 1
            
        self.ax.scatter(X, Y, Z, c=rgba_colors, marker='o')
        self.ax.set_xlabel(f'Criterion {criterion_index + 1}')
        self.ax.set_zlabel('\n\n\nProduct of all \n criteria values')
        self.ax.set_ylabel('\n\n\nProduct of \n other criteria')
        self.draw()

    def _get_color_gradient(self, index, total):
        """
        Return color in gradient from green to red
        """
        normalized_index = index / (total - 1) if total > 1 else 0
        green = np.array(mcolors.to_rgba('green', alpha=1)[:3])
        red = np.array(mcolors.to_rgba('red', alpha=1)[:3])
        return green * (1 - normalized_index) + red * normalized_index
        
    def save_plot(self, filename):
        """
        Save the current plot to file
        """
        self.fig.savefig(filename)
        # Show success message
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Chart saved successfully!")
        msg.setInformativeText(f"File saved as: {filename}")
        msg.setWindowTitle("Saving Chart")
        msg.exec_()


def create_ranking_chart(ranks: List[int], method_name: str, title: Optional[str] = None):
    """
    Create a ranking chart showing the order of alternatives
    
    Args:
        ranks: Ranking of alternatives
        method_name: Name of the method used
        title: Optional custom title
        
    Returns:
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if not title:
        title = f'Alternative Rankings - {method_name}'
        
    ax.bar(range(len(ranks)), [len(ranks)-r for r in ranks], tick_label=[f'A{i+1}' for i in range(len(ranks))])
    ax.set_title(title)
    ax.set_xlabel('Alternatives')
    ax.set_ylabel('Rank')
    ax.invert_yaxis()  # Higher rank (better) at top
    
    return fig


def create_comparison_chart(all_ranks: dict, title: Optional[str] = None):
    """
    Create a comparison chart showing rankings across different methods
    
    Args:
        all_ranks: Dictionary with method names as keys and rankings as values
        title: Optional custom title
        
    Returns:
        Matplotlib figure object
    """
    if not all_ranks:
        return None
        
    fig, ax = plt.subplots(figsize=(12, 6))
    
    if not title:
        title = 'Comparison of Alternative Rankings Across Methods'
        
    # Prepare data
    methods = list(all_ranks.keys())
    n_alternatives = len(all_ranks[methods[0]])
    alternatives = [f'A{i+1}' for i in range(n_alternatives)]
    
    # Create positions for grouped bars
    x = np.arange(n_alternatives)
    width = 0.8 / len(methods)  # Width of bars
    
    for i, method in enumerate(methods):
        ranks = all_ranks[method]
        # Convert to visual rank (higher number = worse rank)
        visual_ranks = [n_alternatives - r for r in ranks]
        offset = (i - len(methods)/2) * width
        ax.bar(x + offset, visual_ranks, width, label=method)
    
    ax.set_title(title)
    ax.set_xlabel('Alternatives')
    ax.set_ylabel('Rank')
    ax.set_xticks(x)
    ax.set_xticklabels(alternatives)
    ax.legend()
    ax.invert_yaxis()  # Better ranks at top
    
    return fig


def create_weights_visualization(weights: List[float], criteria_names: Optional[List[str]] = None):
    """
    Create a visualization of criteria weights
    
    Args:
        weights: List of weights for each criterion
        criteria_names: Optional list of criterion names
        
    Returns:
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if not criteria_names:
        criteria_names = [f'C{i+1}' for i in range(len(weights))]
    
    ax.bar(criteria_names, weights)
    ax.set_title('Criteria Weights Distribution')
    ax.set_xlabel('Criteria')
    ax.set_ylabel('Weight')
    
    # Add value labels on bars
    for i, v in enumerate(weights):
        ax.text(i, v + 0.01, f'{v:.2f}', ha='center', va='bottom')
    
    return fig


def create_performance_spider_chart(alternative_scores: List[List[float]], 
                                   method_name: str, 
                                   criteria_names: Optional[List[str]] = None):
    """
    Create a spider/radar chart showing performance of alternatives across criteria
    
    Args:
        alternative_scores: Matrix of scores for each alternative on each criterion
        method_name: Name of the method used
        criteria_names: Optional list of criterion names
        
    Returns:
        Matplotlib figure object
    """
    if not alternative_scores:
        return None
        
    n_criteria = len(alternative_scores[0])
    if not criteria_names:
        criteria_names = [f'C{i+1}' for i in range(n_criteria)]
    
    # Normalize scores to 0-1 range for visualization
    scores_array = np.array(alternative_scores)
    min_vals = np.min(scores_array, axis=0)
    max_vals = np.max(scores_array, axis=0)
    
    # Handle case where min equals max
    range_vals = max_vals - min_vals
    range_vals[range_vals == 0] = 1
    normalized_scores = (scores_array - min_vals) / range_vals
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    # Compute angle for each criterion
    angles = np.linspace(0, 2 * np.pi, n_criteria, endpoint=False).tolist()
    angles += angles[:1]  # Complete the circle
    
    # Draw one axe per variable + add labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(criteria_names)
    
    # Draw ylabels
    ax.set_ylim(0, 1)
    
    # Plot each alternative
    for i, scores in enumerate(normalized_scores):
        values = scores.tolist()
        values += values[:1]  # Complete the circle
        ax.plot(angles, values, linewidth=1, linestyle='solid', label=f'A{i+1}')
        ax.fill(angles, values, alpha=0.25)
    
    ax.set_title(f'Performance Spider Chart - {method_name}')
    ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))
    
    return fig