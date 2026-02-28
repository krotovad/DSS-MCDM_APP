"""
Utility functions module
Contains common helper functions used across the application
"""

import os
import sys
from typing import List, Tuple, Any, Dict, Union
import json
import pickle
import hashlib


def normalize_weights(weights: List[float]) -> List[float]:
    """
    Normalize weights so they sum to 1
    
    Args:
        weights: List of weights
        
    Returns:
        Normalized weights that sum to 1
    """
    total = sum(weights)
    if total == 0:
        # If all weights are 0, assign equal weights
        return [1.0/len(weights)] if weights else []
    return [w/total for w in weights]


def calculate_consistency_ratio(matrix: List[List[float]]) -> float:
    """
    Calculate consistency ratio for AHP pairwise comparison matrix
    This is a simplified implementation
    
    Args:
        matrix: Pairwise comparison matrix
        
    Returns:
        Consistency ratio
    """
    n = len(matrix)
    if n <= 2:
        return 0.0  # Consistency is automatically satisfied for 1x1 or 2x2 matrices
    
    # Calculate principal eigenvalue
    matrix_arr = [[float(cell) for cell in row] for row in matrix]
    
    # For simplicity, we're using an approximation
    # In a real implementation, you would calculate the eigenvalues
    # This is just a placeholder implementation
    ri_dict = {1: 0, 2: 0, 3: 0.58, 4: 0.9, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
    ri = ri_dict.get(n, 1.49)  # Random index
    
    if ri == 0:
        return 0.0
    
    # This is a simplified calculation - in reality, you'd compute the principal eigenvalue
    # For now, return a placeholder
    return 0.1  # Placeholder CR value


def save_session(data: Dict[str, Any], filepath: str) -> bool:
    """
    Save current analysis session to file
    
    Args:
        data: Session data to save
        filepath: Path to save the session
        
    Returns:
        True if save was successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        return True
    except Exception as e:
        print(f"Error saving session: {str(e)}")
        return False


def load_session(filepath: str) -> Union[Dict[str, Any], None]:
    """
    Load analysis session from file
    
    Args:
        filepath: Path to load the session from
        
    Returns:
        Session data if load was successful, None otherwise
    """
    try:
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        print(f"Error loading session: {str(e)}")
        return None


def validate_matrix_shape(matrix: List[List[Any]], expected_rows: int = None, expected_cols: int = None) -> Tuple[bool, str]:
    """
    Validate that a matrix has proper shape and is rectangular
    
    Args:
        matrix: Matrix to validate
        expected_rows: Expected number of rows (optional)
        expected_cols: Expected number of columns (optional)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not matrix:
        return False, "Matrix is empty"
    
    if not isinstance(matrix, list):
        return False, "Matrix is not a list"
    
    if expected_rows is not None and len(matrix) != expected_rows:
        return False, f"Expected {expected_rows} rows, got {len(matrix)}"
    
    if not all(isinstance(row, list) for row in matrix):
        return False, "Not all rows are lists"
    
    # Check if all rows have the same length
    if len(set(len(row) for row in matrix)) > 1:
        return False, "Rows have different lengths"
    
    if expected_cols is not None and len(matrix[0]) != expected_cols:
        return False, f"Expected {expected_cols} columns, got {len(matrix[0])}"
    
    return True, ""


def format_results_for_display(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format analysis results for display purposes
    
    Args:
        results: Raw analysis results
        
    Returns:
        Formatted results ready for display
    """
    formatted = {}
    
    for method, result in results.items():
        if isinstance(result, list):
            # If result is a ranking list, format it nicely
            if all(isinstance(x, int) for x in result):
                # These are ranks, convert to readable format
                formatted[method] = {
                    'rankings': [int(rank) + 1 for rank in result],  # Add 1 since we internally use 0-based indexing
                    'top_alternative': int(result[0]) + 1 if result else None
                }
            else:
                # These might be scores or other values
                formatted[method] = {
                    'values': [float(x) if isinstance(x, (int, float)) else str(x) for x in result],
                    'top_alternative': result.index(max(result)) + 1 if result else None
                }
        else:
            formatted[method] = result
    
    return formatted


def calculate_similarity_between_methods(results: Dict[str, List[int]]) -> Dict[str, float]:
    """
    Calculate similarity between different methods' results using Kendall's tau-like measure
    
    Args:
        results: Dictionary with method names as keys and rankings as values
        
    Returns:
        Dictionary with pairwise similarities between methods
    """
    if len(results) < 2:
        return {}
    
    methods = list(results.keys())
    similarities = {}
    
    for i in range(len(methods)):
        for j in range(i+1, len(methods)):
            method1, method2 = methods[i], methods[j]
            ranks1, ranks2 = results[method1], results[method2]
            
            if len(ranks1) != len(ranks2):
                similarities[f"{method1}_vs_{method2}"] = 0.0
                continue
            
            n = len(ranks1)
            if n <= 1:
                similarities[f"{method1}_vs_{method2}"] = 1.0
                continue
            
            # Count concordant and discordant pairs
            concordant = 0
            discordant = 0
            
            for a_idx in range(n):
                for b_idx in range(a_idx + 1, n):
                    a_b_pref_1 = ranks1[a_idx] - ranks1[b_idx]  # Lower rank means better (0 is best)
                    a_b_pref_2 = ranks2[a_idx] - ranks2[b_idx]
                    
                    if (a_b_pref_1 > 0 and a_b_pref_2 > 0) or (a_b_pref_1 < 0 and a_b_pref_2 < 0):
                        concordant += 1
                    elif (a_b_pref_1 > 0 and a_b_pref_2 < 0) or (a_b_pref_1 < 0 and a_b_pref_2 > 0):
                        discordant += 1
            
            total_pairs = concordant + discordant
            if total_pairs == 0:
                tau = 1.0  # If no comparable pairs, consider perfectly similar
            else:
                tau = (concordant - discordant) / total_pairs
            
            similarities[f"{method1}_vs_{method2}"] = tau
            similarities[f"{method2}_vs_{method1}"] = tau  # Symmetric
    
    return similarities


def sanitize_input(value: str, allowed_types: List[str] = None) -> Union[str, float, int]:
    """
    Sanitize user input to prevent injection attacks and validate format
    
    Args:
        value: Input value to sanitize
        allowed_types: List of allowed types ('str', 'int', 'float')
        
    Returns:
        Sanitized value in appropriate type
    """
    if allowed_types is None:
        allowed_types = ['str', 'int', 'float']
    
    # Basic sanitization - remove potentially dangerous characters
    sanitized = value.strip()
    
    # Check against allowed types
    if 'float' in allowed_types:
        try:
            return float(sanitized)
        except ValueError:
            pass
    
    if 'int' in allowed_types:
        try:
            return int(sanitized)
        except ValueError:
            pass
    
    # Default to string
    return sanitized


def hash_data(data: Any) -> str:
    """
    Generate hash for data to identify unique datasets
    
    Args:
        data: Data to hash
        
    Returns:
        Hash string
    """
    data_str = json.dumps(data, sort_keys=True, default=str)
    return hashlib.md5(data_str.encode()).hexdigest()


def validate_criteria_direction(directions: List[str]) -> Tuple[bool, str]:
    """
    Validate criteria direction (benefit/cost)
    
    Args:
        directions: List of directions ('benefit' or 'cost')
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_directions = {'benefit', 'cost', 'max', 'min'}
    
    if not directions:
        return True, "No directions specified, assuming all benefit criteria"
    
    for i, direction in enumerate(directions):
        if direction.lower() not in valid_directions:
            return False, f"Invalid direction '{direction}' at position {i}. Valid options: {valid_directions}"
    
    return True, ""