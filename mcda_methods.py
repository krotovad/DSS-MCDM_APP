"""
MCDA Methods module
Contains implementations of various Multi-Criteria Decision Analysis methods
"""

import numpy as np
import math


def normalize_matrix(matrix):
    """Normalize decision matrix using vector normalization"""
    matrix = np.array(matrix, dtype=float)
    norm_matrix = np.zeros_like(matrix)
    
    for j in range(matrix.shape[1]):
        col_sum_sq = np.sum(matrix[:, j] ** 2)
        if col_sum_sq != 0:
            norm_matrix[:, j] = matrix[:, j] / math.sqrt(col_sum_sq)
        else:
            norm_matrix[:, j] = matrix[:, j]
    
    return norm_matrix


def topsis(matrix, weights):
    """
    TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)
    
    Args:
        matrix: Decision matrix (alternatives x criteria)
        weights: Criteria weights
    
    Returns:
        List of rankings for each alternative
    """
    matrix = np.array(matrix, dtype=float)
    weights = np.array(weights, dtype=float)
    
    # Normalize the matrix
    norm_matrix = normalize_matrix(matrix)
    
    # Weight the normalized matrix
    weighted_matrix = norm_matrix * weights
    
    # Find positive and negative ideal solutions
    ideal_positive = np.max(weighted_matrix, axis=0)
    ideal_negative = np.min(weighted_matrix, axis=0)
    
    # Calculate distances to ideal solutions
    dist_positive = np.sqrt(np.sum((weighted_matrix - ideal_positive) ** 2, axis=1))
    dist_negative = np.sqrt(np.sum((weighted_matrix - ideal_negative) ** 2, axis=1))
    
    # Calculate relative closeness to ideal solution
    scores = dist_negative / (dist_positive + dist_negative)
    
    # Rank alternatives by score (higher is better)
    ranks = np.argsort(-scores).tolist()  # Negative for descending order
    return ranks


def wsr(matrix, weights):
    """
    Weighted Sum Model (WSM)
    
    Args:
        matrix: Decision matrix (alternatives x criteria)
        weights: Criteria weights
    
    Returns:
        List of rankings for each alternative
    """
    matrix = np.array(matrix, dtype=float)
    weights = np.array(weights, dtype=float)
    
    # Calculate weighted sum for each alternative
    scores = np.sum(matrix * weights, axis=1)
    
    # Rank alternatives by score (higher is better)
    ranks = np.argsort(-scores).tolist()  # Negative for descending order
    return ranks


def electre_iv(matrix):
    """
    ELECTRE IV method (without weights)
    
    Args:
        matrix: Decision matrix (alternatives x criteria)
    
    Returns:
        List of rankings for each alternative
    """
    matrix = np.array(matrix, dtype=float)
    
    # Normalize the matrix using min-max normalization
    mins = np.min(matrix, axis=0)
    maxs = np.max(matrix, axis=0)
    ranges = maxs - mins
    
    # Handle case where all values in a column are the same
    ranges[ranges == 0] = 1
    normalized_matrix = (matrix - mins) / ranges
    
    n_alt, n_crit = normalized_matrix.shape
    
    # Define thresholds
    q = [0.1] * n_crit  # Indifference threshold
    p = [0.3] * n_crit  # Preference threshold
    v = [0.5] * n_crit  # Veto threshold
    
    # Concordance matrix
    concordance = np.zeros((n_alt, n_alt))
    for i in range(n_alt):
        for j in range(n_alt):
            if i != j:
                s = 0
                total_weight = n_crit
                for k in range(n_crit):
                    diff = normalized_matrix[j, k] - normalized_matrix[i, k]
                    if diff >= p[k]:
                        s += 0
                    elif diff <= q[k]:
                        s += 1
                    else:
                        s += (p[k] - diff) / (p[k] - q[k])
                concordance[i, j] = s / total_weight
    
    # Discordance matrix
    discordance = np.zeros((n_alt, n_alt))
    for i in range(n_alt):
        for j in range(n_alt):
            if i != j:
                max_diff = 0
                max_range = 0
                for k in range(n_crit):
                    diff = normalized_matrix[j, k] - normalized_matrix[i, k]
                    if p[k] != 0:
                        curr_diff = max(0, diff - p[k]) / (v[k] - p[k])
                        if curr_diff > max_diff:
                            max_diff = curr_diff
                discordance[i, j] = max_diff
    
    # Outranking relations
    credibility = np.zeros((n_alt, n_alt))
    for i in range(n_alt):
        for j in range(n_alt):
            if i != j:
                credibility[i, j] = concordance[i, j] * (1 - discordance[i, j])
    
    # Calculate dominance counts
    dominance_count = np.sum(credibility > 0.5, axis=1)
    ranks = np.argsort(-dominance_count).tolist()
    
    return ranks


def Vikor(matrix, weights):
    """
    VIKOR (VlseKriterijumska Optimizacija I Kompromisno Resenje)
    
    Args:
        matrix: Decision matrix (alternatives x criteria)
        weights: Criteria weights
    
    Returns:
        List of rankings for each alternative
    """
    matrix = np.array(matrix, dtype=float)
    weights = np.array(weights, dtype=float)
    
    # Determine best and worst values for each criterion
    f_best = np.max(matrix, axis=0)  # Assuming higher is better
    f_worst = np.min(matrix, axis=0)
    
    # Calculate Si and Ri values
    n_alt = matrix.shape[0]
    S = np.zeros(n_alt)
    R = np.zeros(n_alt)
    
    for i in range(n_alt):
        diffs = f_best - matrix[i, :]
        weighted_diffs = weights * diffs / (f_best - f_worst + 1e-10)  # Adding small value to avoid division by zero
        S[i] = np.sum(weighted_diffs)
        R[i] = np.max(weighted_diffs)
    
    # Normalize Si and Ri
    S_best = np.min(S)
    S_worst = np.max(S)
    R_best = np.min(R)
    R_worst = np.max(R)
    
    if S_best == S_worst:
        Q = np.zeros(n_alt)
    else:
        v = 0.5  # Strategy weight
        Q = v * (S - S_best) / (S_worst - S_best + 1e-10) + (1 - v) * (R - R_best) / (R_worst - R_best + 1e-10)
    
    # Rank by Q values (lower is better)
    ranks = np.argsort(Q).tolist()
    return ranks


def ahp(matrix, weights):
    """
    Analytic Hierarchy Process (AHP)
    
    Args:
        matrix: Decision matrix (alternatives x criteria)
        weights: Criteria weights
    
    Returns:
        List of rankings for each alternative
    """
    matrix = np.array(matrix, dtype=float)
    weights = np.array(weights, dtype=float)
    
    # Calculate weighted sum for each alternative
    scores = np.sum(matrix * weights, axis=1)
    
    # Rank alternatives by score (higher is better)
    ranks = np.argsort(-scores).tolist()  # Negative for descending order
    return ranks


def chp(matrix, weights):
    """
    Consensus Hallucination Process (CHP) - Simplified version
    
    Args:
        matrix: Decision matrix (alternatives x criteria)
        weights: Criteria weights
    
    Returns:
        List of rankings for each alternative
    """
    matrix = np.array(matrix, dtype=float)
    weights = np.array(weights, dtype=float)
    
    # Calculate weighted sum for each alternative
    scores = np.sum(matrix * weights, axis=1)
    
    # Calculate consistency ratio (simplified)
    # For this implementation, we'll just rank by scores
    ranks = np.argsort(-scores).tolist()  # Negative for descending order
    return ranks


def minsum(matrix):
    """
    Minimum Sum Method
    
    Args:
        matrix: Decision matrix (alternatives x criteria)
    
    Returns:
        List of rankings for each alternative
    """
    matrix = np.array(matrix, dtype=float)
    
    # Calculate sum for each alternative
    sums = np.sum(matrix, axis=1)
    
    # Rank alternatives by sum (lower is better)
    ranks = np.argsort(sums).tolist()
    return ranks


def minmax(matrix):
    """
    Minimax Method
    
    Args:
        matrix: Decision matrix (alternatives x criteria)
    
    Returns:
        List of rankings for each alternative
    """
    matrix = np.array(matrix, dtype=float)
    
    # Find maximum value for each alternative
    max_values = np.max(matrix, axis=1)
    
    # Rank alternatives by max value (lower is better)
    ranks = np.argsort(max_values).tolist()
    return ranks


def maxmin(matrix):
    """
    Maximin Method
    
    Args:
        matrix: Decision matrix (alternatives x criteria)
    
    Returns:
        List of rankings for each alternative
    """
    matrix = np.array(matrix, dtype=float)
    
    # Find minimum value for each alternative
    min_values = np.min(matrix, axis=1)
    
    # Rank alternatives by min value (higher is better)
    ranks = np.argsort(-min_values).tolist()  # Negative for descending order
    return ranks


def dip(matrix):
    """
    Distance to Ideal Point Method
    
    Args:
        matrix: Decision matrix (alternatives x criteria)
    
    Returns:
        List of rankings for each alternative
    """
    matrix = np.array(matrix, dtype=float)
    
    # Find ideal point (maximum for each criterion)
    ideal_point = np.max(matrix, axis=0)
    
    # Calculate Euclidean distance to ideal point for each alternative
    distances = np.sqrt(np.sum((matrix - ideal_point) ** 2, axis=1))
    
    # Rank alternatives by distance (lower is better)
    ranks = np.argsort(distances).tolist()
    return ranks


def orp(matrix):
    """
    Generalized Decision Rule (Обобщенное решающее правило)
    
    Args:
        matrix: Decision matrix (alternatives x criteria)
    
    Returns:
        List of rankings for each alternative
    """
    matrix = np.array(matrix, dtype=float)
    
    # Normalize the matrix using vector normalization
    norm_matrix = normalize_matrix(matrix)
    
    # Apply multiple methods and combine results
    # Using MINSUM, MAXMIN, and DIP for the combination
    
    # Calculate scores using different approaches
    minsum_scores = np.sum(norm_matrix, axis=1)
    maxmin_scores = np.min(norm_matrix, axis=1)
    dip_distances = np.sqrt(np.sum((norm_matrix - np.max(norm_matrix, axis=0)) ** 2, axis=1))
    
    # Combine scores: lower values indicate better performance in all measures
    combined_scores = minsum_scores + (1 / (maxmin_scores + 1e-10)) + dip_distances
    
    # Rank alternatives by combined score (lower is better)
    ranks = np.argsort(combined_scores).tolist()
    return ranks


def promethee_ii(matrix, weights):
    """
    PROMETHEE II (Preference Ranking Organization METHod for Enrichment Evaluation)
    
    Args:
        matrix: Decision matrix (alternatives x criteria)
        weights: Criteria weights
    
    Returns:
        List of rankings for each alternative
    """
    matrix = np.array(matrix, dtype=float)
    weights = np.array(weights, dtype=float)
    
    n_alt, n_crit = matrix.shape
    
    # Calculate preference functions for each criterion
    P = np.zeros((n_alt, n_alt, n_crit))
    
    for k in range(n_crit):
        for i in range(n_alt):
            for j in range(n_alt):
                # Using linear preference function
                diff = matrix[j, k] - matrix[i, k]
                
                if diff <= 0:
                    P[i, j, k] = 0
                else:
                    # Normalize the difference based on the range of the criterion
                    max_val = np.max(matrix[:, k])
                    min_val = np.min(matrix[:, k])
                    
                    if max_val != min_val:
                        normalized_diff = diff / (max_val - min_val)
                        P[i, j, k] = min(1, normalized_diff)
                    else:
                        P[i, j, k] = 0
    
    # Calculate global preference index
    pi_matrix = np.zeros((n_alt, n_alt))
    for i in range(n_alt):
        for j in range(n_alt):
            if i != j:
                pi_matrix[i, j] = np.sum(weights * P[i, j, :])
    
    # Calculate leaving and entering flows
    leaving_flow = np.sum(pi_matrix, axis=1) / (n_alt - 1)  # How much each alternative outranks others
    entering_flow = np.sum(pi_matrix, axis=0) / (n_alt - 1)  # How much each alternative is outranked by others
    
    # Net flow
    net_flow = leaving_flow - entering_flow
    
    # Rank by net flow (higher is better)
    ranks = np.argsort(-net_flow).tolist()
    
    return ranks


def grey_relational_analysis(matrix, weights):
    """
    Grey Relational Analysis (GRA)
    
    Args:
        matrix: Decision matrix (alternatives x criteria)
        weights: Criteria weights
    
    Returns:
        List of rankings for each alternative
    """
    matrix = np.array(matrix, dtype=float)
    weights = np.array(weights, dtype=float)
    
    n_alt, n_crit = matrix.shape
    
    # Normalize the decision matrix
    # For benefit criteria, use min-max normalization
    normalized_matrix = np.zeros_like(matrix)
    for j in range(n_crit):
        min_val = np.min(matrix[:, j])
        max_val = np.max(matrix[:, j])
        if max_val != min_val:
            normalized_matrix[:, j] = (matrix[:, j] - min_val) / (max_val - min_val)
        else:
            normalized_matrix[:, j] = 1.0  # If all values are the same
    
    # Determine reference sequence (best values for each criterion)
    reference_sequence = np.max(normalized_matrix, axis=0)
    
    # Calculate deviation sequences
    deviation_matrix = np.abs(normalized_matrix - reference_sequence)
    
    # Calculate grey relational coefficients
    min_dev = np.min(deviation_matrix)
    max_dev = np.max(deviation_matrix)
    
    # Distinguish coefficient
    zeta = 0.5
    
    grey_rel_coeff = (min_dev + zeta * max_dev) / (deviation_matrix + zeta * max_dev)
    
    # Calculate weighted grey relational grades
    grey_grades = np.zeros(n_alt)
    for i in range(n_alt):
        grey_grades[i] = np.sum(weights * grey_rel_coeff[i, :])
    
    # Rank by grey relational grade (higher is better)
    ranks = np.argsort(-grey_grades).tolist()
    
    return ranks


def fuzzy_ahp(matrix, weights):
    """
    Fuzzy Analytic Hierarchy Process (F-AHP)
    Simplified implementation using triangular fuzzy numbers
    
    Args:
        matrix: Decision matrix (alternatives x criteria)
        weights: Criteria weights
    
    Returns:
        List of rankings for each alternative
    """
    matrix = np.array(matrix, dtype=float)
    weights = np.array(weights, dtype=float)
    
    n_alt, n_crit = matrix.shape
    
    # Convert crisp values to fuzzy numbers and back for demonstration
    # In a real implementation, we would handle fuzzy comparison matrices
    # Here we'll just apply fuzzy-like transformations to the weights
    
    # Normalize the decision matrix
    normalized_matrix = np.zeros_like(matrix)
    for j in range(n_crit):
        col_sum = np.sum(matrix[:, j])
        if col_sum != 0:
            normalized_matrix[:, j] = matrix[:, j] / col_sum
        else:
            normalized_matrix[:, j] = matrix[:, j]
    
    # Calculate fuzzy synthetic extent (simplified approach)
    # Apply weights and compute scores
    weighted_scores = np.zeros(n_alt)
    for i in range(n_alt):
        weighted_scores[i] = np.sum(weights * normalized_matrix[i, :])
    
    # Rank by weighted scores (higher is better)
    ranks = np.argsort(-weighted_scores).tolist()
    
    return ranks


def dematel(matrix, weights):
    """
    DEMATEL (Decision Making Trial and Evaluation Laboratory)
    Simplified implementation focusing on direct relation matrix
    
    Args:
        matrix: Decision matrix (alternatives x criteria)
        weights: Criteria weights
    
    Returns:
        List of rankings for each alternative
    """
    matrix = np.array(matrix, dtype=float)
    weights = np.array(weights, dtype=float)
    
    n_alt, n_crit = matrix.shape
    
    # For DEMATEL, we typically work with a relationship matrix
    # Since we have alternatives vs criteria, we'll adapt the method
    # Create a direct relation matrix based on normalized values
    
    # Normalize the matrix to [0,1] range
    normalized_matrix = np.zeros_like(matrix)
    for j in range(n_crit):
        min_val = np.min(matrix[:, j])
        max_val = np.max(matrix[:, j])
        if max_val != min_val:
            normalized_matrix[:, j] = (matrix[:, j] - min_val) / (max_val - min_val)
        else:
            normalized_matrix[:, j] = 1.0
    
    # Create a weighted influence matrix
    # Each alternative influences criteria based on its performance and weights
    influence_matrix = normalized_matrix * weights
    
    # Calculate total influence for each alternative
    total_influence = np.sum(influence_matrix, axis=1)
    
    # Rank by total influence (higher is better)
    ranks = np.argsort(-total_influence).tolist()
    
    return ranks


class MCDAData:
    """
    Класс для хранения данных для MCDA анализа
    """
    
    def __init__(self, matrix, weights, criteria_names=None, alternatives_names=None):
        self.matrix = np.array(matrix, dtype=float)
        self.weights = np.array(weights, dtype=float)
        self.criteria_names = criteria_names or [f"Criterion_{i+1}" for i in range(len(weights))]
        self.alternatives_names = alternatives_names or [f"Alternative_{i+1}" for i in range(len(matrix))]


def perform_analysis(data, methods, weights):
    """
    Perform analysis using selected methods
    
    Args:
        data: Decision matrix (alternatives x criteria)
        methods: List of method names to use
        weights: Criteria weights
    
    Returns:
        Dictionary with results for each method
    """
    results = {}
    
    for method in methods:
        try:
            if method == 'TOPSIS':
                results[method] = topsis(data, weights)
            elif method == 'WSR':
                results[method] = wsr(data, weights)
            elif method == 'ELECTRE':
                results[method] = electre_iv(data)
            elif method == 'VIKOR':
                results[method] = Vikor(data, weights)
            elif method == 'AHP':
                results[method] = ahp(data, weights)
            elif method == 'CHP':
                results[method] = chp(data, weights)
            elif method == 'MINSUM':
                results[method] = minsum(data)
            elif method == 'MINMAX':
                results[method] = minmax(data)
            elif method == 'MAXMIN':
                results[method] = maxmin(data)
            elif method == 'DIP':
                results[method] = dip(data)
            elif method == 'ОРП':
                results[method] = orp(data)
            elif method == 'PROMETHEE':
                results[method] = promethee_ii(data, weights)
            elif method == 'GRA':
                results[method] = grey_relational_analysis(data, weights)
            elif method == 'F-AHP':
                results[method] = fuzzy_ahp(data, weights)
            elif method == 'DEMATEL':
                results[method] = dematel(data, weights)
            else:
                print(f"Method {method} not implemented")
                results[method] = []
        except Exception as e:
            print(f"Error in method {method}: {str(e)}")
            results[method] = []
    
    return results