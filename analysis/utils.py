"""
Fonctions utilitaires pour l'analyse des résultats
"""

import json
import pandas as pd
import numpy as np


def load_benchmark_results(filepath):
    """Charge les résultats de benchmark depuis un fichier JSON"""
    with open(filepath, 'r') as f:
        return json.load(f)


def results_to_dataframe(results):
    """Convertit les résultats en DataFrame pandas"""
    data = []
    for result in results:
        row = {
            'algorithm': result['algorithm'],
            'problem': result['problem'],
            'problem_size': result['problem_size'],
            'instance_id': result['instance_id'],
            'success': result['success'],
            'time_ms': result['metrics']['time_ms'],
            'memory_kb': result['metrics']['memory_kb'],
            'nodes_visited': result['metrics']['nodes_visited'],
            'nodes_generated': result['metrics']['nodes_generated'],
            'solution_length': result['metrics']['solution_length'],
        }
        data.append(row)
    
    return pd.DataFrame(data)


def calculate_statistics(df, metric='time_ms'):
    """Calcule les statistiques descriptives pour une métrique"""
    stats = df.groupby(['algorithm', 'problem'])[metric].agg([
        'count',
        'mean',
        'std',
        'min',
        'max',
        ('q25', lambda x: x.quantile(0.25)),
        ('median', lambda x: x.quantile(0.5)),
        ('q75', lambda x: x.quantile(0.75))
    ])
    
    return stats


def compare_algorithms(df, metric='time_ms', problem=None):
    """Compare les algorithmes sur une métrique spécifique"""
    if problem:
        df = df[df['problem'] == problem]
    
    comparison = df.groupby('algorithm')[metric].agg(['mean', 'std', 'min', 'max'])
    comparison = comparison.sort_values('mean')
    
    return comparison


def find_best_algorithm(df, metric='time_ms', problem=None, minimize=True):
    """Trouve le meilleur algorithme pour une métrique donnée"""
    if problem:
        df = df[df['problem'] == problem]
    
    avg_metric = df.groupby('algorithm')[metric].mean()
    
    if minimize:
        best = avg_metric.idxmin()
        value = avg_metric.min()
    else:
        best = avg_metric.idxmax()
        value = avg_metric.max()
    
    return best, value


def calculate_speedup(df, baseline_algo, comparison_algo, metric='time_ms'):
    """Calcule le speedup d'un algorithme par rapport à un baseline"""
    baseline_data = df[df['algorithm'] == baseline_algo][metric].mean()
    comparison_data = df[df['algorithm'] == comparison_algo][metric].mean()
    
    if comparison_data == 0:
        return float('inf')
    
    speedup = baseline_data / comparison_data
    return speedup


def filter_successful_runs(df):
    """Filtre pour ne garder que les exécutions réussies"""
    return df[df['success'] == True]


def group_by_problem_size(df, metric='time_ms'):
    """Regroupe les résultats par taille de problème"""
    return df.groupby(['algorithm', 'problem_size'])[metric].mean().unstack()


def export_to_csv(df, filename):
    """Exporte le DataFrame en CSV"""
    df.to_csv(filename, index=False)
    print(f"✓ Données exportées vers: {filename}")


def export_to_latex(df, filename):
    """Exporte le DataFrame en table LaTeX"""
    latex = df.to_latex(index=False, float_format="%.2f")
    with open(filename, 'w') as f:
        f.write(latex)
    print(f"✓ Table LaTeX exportée vers: {filename}")
