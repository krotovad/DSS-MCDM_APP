import PySimpleGUI as sg
import random
import numpy as np

# Function to generate random weights that sum up to 1
def generate_weights(n):
    random_weights = [random.random() for _ in range(n)]
    total_sum = sum(random_weights)
    return [w / total_sum for w in random_weights]

# Generate random alternative with more sparse values
def generate_random_alternative():
    return [random.randint(1, 100) for _ in range(3)]

# WSR Function
def wsr(weights, alternatives):
    scores = []
    for i, alternative in enumerate(alternatives):
        score = sum(w * v for w, v in zip(weights, alternative))
        scores.append((i+1, round(score, 3)))
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores

# TOPSIS Function
def topsis(weights, alternatives):
    normalized_matrix = np.array(alternatives) / np.sqrt(np.sum(np.square(alternatives), axis=0))
    weighted_matrix = normalized_matrix * weights
    ideal_positive = np.max(weighted_matrix, axis=0)
    ideal_negative = np.min(weighted_matrix, axis=0)
    dist_pos = np.sqrt(np.sum(np.square(weighted_matrix - ideal_positive), axis=1))
    dist_neg = np.sqrt(np.sum(np.square(weighted_matrix - ideal_negative), axis=1))
    closeness = dist_neg / (dist_neg + dist_pos)
    sorted_indices = np.argsort(closeness)[::-1]
    return [(i+1, round(closeness[i], 3)) for i in sorted_indices]

# ELECTRE Function
def electre(weights, alternatives):
    weighted_matrix = np.array(alternatives) * weights
    max_values = np.max(weighted_matrix, axis=0)
    threshold = 0.8 * max_values
    outranking = np.sum(weighted_matrix[:, None, :] >= threshold, axis=2)
    outranking = np.sum(outranking > (outranking.shape[1] // 2), axis=1)
    sorted_indices = np.argsort(outranking)[::-1]
    return [(i+1, round(outranking[i], 3)) for i in sorted_indices]


# VIKOR Function
def vikor(weights, alternatives):
    weighted_matrix = np.array(alternatives) * weights
    ideal_best = np.max(weighted_matrix, axis=0)
    ideal_worst = np.min(weighted_matrix, axis=0)
    S = np.sum(ideal_best - weighted_matrix, axis=1)
    R = np.max(ideal_best - weighted_matrix, axis=1)
    S_best = np.min(S)
    S_worst = np.max(S)
    R_best = np.min(R)
    R_worst = np.max(R)
    Q = 0.5 * (S - S_best) / (S_worst - S_best) + 0.5 * (R - R_best) / (R_worst - R_best)
    sorted_indices = np.argsort(Q)
    return [(i+1, round(Q[i], 3)) for i in sorted_indices]

# Function to mark the best alternatives with an asterisk
def mark_best_alternative(ranking):
    best_score = ranking[0][1]  # Assuming the ranking is already sorted
    return [(f"*" if score == best_score else "", alt, score) for alt, score in ranking]

# Pareto-optimal check
def is_dominated(a, b):
    return all(x >= y for x, y in zip(a, b)) and any(x > y for x, y in zip(a, b))

# Find Pareto-optimal alternatives
def find_pareto_optimal_alternatives(alternatives):
    pareto_optimal_set = []
    for i in range(len(alternatives)):
        is_optimal = True
        for j in range(len(alternatives)):
            if i != j and is_dominated(alternatives[i], alternatives[j]):
                is_optimal = False
                break
        if is_optimal:
            pareto_optimal_set.append((i+1, alternatives[i]))
    return pareto_optimal_set

# Generate random set of alternatives (0 to 30)
n_alternatives = random.randint(0, 30)
alternatives = [generate_random_alternative() for _ in range(n_alternatives)]

# Generate weights
weights = generate_weights(3)

# Get Pareto-optimal alternatives
pareto_optimal_set = find_pareto_optimal_alternatives(alternatives)
pareto_optimal_for_table = [(idx, *alt) for idx, alt in pareto_optimal_set]

# Apply WSR and TOPSIS to Pareto-optimal alternatives
wsr_result = wsr(weights, [alt for idx, alt in pareto_optimal_set])
topsis_result = topsis(weights, [alt for idx, alt in pareto_optimal_set])

# Apply ELECTRE and VIKOR to Pareto-optimal alternatives
electre_result = electre(weights, [alt for idx, alt in pareto_optimal_set])
vikor_result = vikor(weights, [alt for idx, alt in pareto_optimal_set])

# Prepare the first table data
first_table_data = [[i + 1] + [val for sublist in zip(alt, weights) for val in sublist] for i, alt in enumerate(alternatives)]

# Create layout
layout = [
    [sg.Table(values=first_table_data, headings=['Alternative', 'Criteria 1', 'Weight 1', 'Criteria 2', 'Weight 2', 'Criteria 3', 'Weight 3'], 
              display_row_numbers=False, auto_size_columns=True, num_rows=min(25, len(first_table_data)), justification='center')],
    [sg.Text("Pareto-Optimal Alternatives", justification='center')],
    [sg.Table(values=pareto_optimal_for_table, headings=['Alternative', 'Criteria 1', 'Criteria 2', 'Criteria 3'], 
              display_row_numbers=False, auto_size_columns=True, num_rows=min(25, len(pareto_optimal_for_table)), justification='center')],
    [sg.Text("Ranking Results (Pareto-Optimal Only)", justification='center')],
    [sg.Table(values=mark_best_alternative(wsr_result), headings=['Best', 'Alternative', 'WSR Score'], 
              display_row_numbers=False, auto_size_columns=False, num_rows=min(25, len(wsr_result)), col_widths=[5, 10, 10], justification='center'),
     sg.Table(values=mark_best_alternative(topsis_result), headings=['Best', 'Alternative', 'TOPSIS Score'], 
              display_row_numbers=False, auto_size_columns=False, num_rows=min(25, len(topsis_result)), col_widths=[5, 10, 10], justification='center'),
     sg.Table(values=mark_best_alternative(electre_result), headings=['Best', 'Alternative', 'ELECTRE Score'], 
              display_row_numbers=False, auto_size_columns=False, num_rows=min(25, len(electre_result)), col_widths=[5, 10, 10], justification='center'),
     sg.Table(values=mark_best_alternative(vikor_result), headings=['Best', 'Alternative', 'VIKOR Score'], 
              display_row_numbers=False, auto_size_columns=False, num_rows=min(25, len(vikor_result)), col_widths=[5, 10, 10], justification='center')
    ]]

# Create window
window = sg.Window('Decision Analysis', layout, finalize=True)

# Event Loop to process "events"
while True:             
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break

window.close()