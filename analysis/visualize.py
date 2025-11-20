"""
Script de visualisation des résultats de benchmarking
Génère des graphiques comparatifs pour analyser les performances des algorithmes
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# Configuration du style
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

class BenchmarkVisualizer:
    def __init__(self, results_file='results/benchmark_results.json'):
        self.results_file = results_file
        self.df = None
        # Extraire le nom de base du fichier (sans extension) et le dossier parent
        results_path = Path(results_file)
        self.base_name = results_path.stem
        self.output_dir = results_path.parent / 'visuals' / self.base_name
        self.load_data()
    
    def load_data(self):
        """Charge les résultats depuis le fichier JSON"""
        with open(self.results_file, 'r') as f:
            results = json.load(f)
        
        # Convertir en DataFrame pandas
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
        
        self.df = pd.DataFrame(data)
        print(f"{len(self.df)} résultats chargés depuis {self.results_file}")
    
    def plot_time_comparison(self, output_dir=None):
        """Graphique comparatif des temps d'exécution"""
        if output_dir is None:
            output_dir = self.output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Filtrer les résultats réussis
        df_success = self.df[self.df['success']]
        
        if df_success.empty:
            print("Warning: Aucun résultat réussi à visualiser")
            return
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Grouper par algorithme et problème
        grouped = df_success.groupby(['algorithm', 'problem'])['time_ms'].agg(['mean', 'std'])
        
        grouped.plot(kind='bar', y='mean', yerr='std', ax=ax, capsize=4)
        ax.set_xlabel('Algorithme - Problème')
        ax.set_ylabel('Temps (ms)')
        ax.set_title('Comparaison des Temps d\'Exécution par Algorithme et Problème')
        ax.legend(['Moyenne', 'Écart-type'])
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        output_path = f'{output_dir}/time_comparison.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Comparaison des temps générée: {output_path}")
        plt.close()
    
    def plot_memory_comparison(self, output_dir=None):
        """Graphique comparatif de l'utilisation mémoire"""
        if output_dir is None:
            output_dir = self.output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        df_success = self.df[self.df['success']]
        
        if df_success.empty:
            return
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        grouped = df_success.groupby(['algorithm', 'problem'])['memory_kb'].agg(['mean', 'std'])
        grouped.plot(kind='bar', y='mean', yerr='std', ax=ax, capsize=4, color='coral')
        ax.set_xlabel('Algorithme - Problème')
        ax.set_ylabel('Mémoire (Ko)')
        ax.set_title('Comparaison de l\'Utilisation Mémoire par Algorithme et Problème')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        output_path = f'{output_dir}/memory_comparison.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Comparaison de la mémoire générée: {output_path}")
        plt.close()
    
    def plot_nodes_comparison(self, output_dir=None):
        """Graphique comparatif du nombre de nœuds visités"""
        if output_dir is None:
            output_dir = self.output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        df_success = self.df[self.df['success']]
        
        if df_success.empty:
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        
        # Nœuds visités
        grouped_visited = df_success.groupby(['algorithm', 'problem'])['nodes_visited'].mean()
        grouped_visited.plot(kind='bar', ax=ax1, color='steelblue')
        ax1.set_xlabel('Algorithme - Problème')
        ax1.set_ylabel('Nombre de Nœuds')
        ax1.set_title('Nœuds Visités (moyenne)')
        ax1.tick_params(axis='x', rotation=45)
        
        # Nœuds générés
        grouped_generated = df_success.groupby(['algorithm', 'problem'])['nodes_generated'].mean()
        grouped_generated.plot(kind='bar', ax=ax2, color='seagreen')
        ax2.set_xlabel('Algorithme - Problème')
        ax2.set_ylabel('Nombre de Nœuds')
        ax2.set_title('Nœuds Générés (moyenne)')
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        output_path = f'{output_dir}/nodes_comparison.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Nœuds comparés généré: {output_path}")
        plt.close()
    
    def plot_success_rate(self, output_dir=None):
        """Graphique du taux de succès par algorithme"""
        if output_dir is None:
            output_dir = self.output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        success_rate = self.df.groupby(['algorithm', 'problem'])['success'].mean() * 100
        success_rate.plot(kind='bar', ax=ax, color='mediumseagreen')
        ax.set_xlabel('Algorithme - Problème')
        ax.set_ylabel('Taux de Succès (%)')
        ax.set_title('Taux de Succès par Algorithme et Problème')
        ax.axhline(y=100, color='red', linestyle='--', alpha=0.5, label='100%')
        ax.legend()
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        output_path = f'{output_dir}/success_rate.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Taux de succès généré: {output_path}")
        plt.close()
    
    def plot_size_scaling(self, output_dir=None):
        """Graphique de l'évolution des performances selon la taille du problème"""
        if output_dir is None:
            output_dir = self.output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        df_success = self.df[self.df['success']]
        
        if df_success.empty or df_success['problem_size'].nunique() < 2:
            print("Warning: Pas assez de tailles différentes pour le graphique de scalabilité")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Temps vs Taille
        for algo in df_success['algorithm'].unique():
            data = df_success[df_success['algorithm'] == algo]
            grouped = data.groupby('problem_size')['time_ms'].mean()
            axes[0, 0].plot(grouped.index, grouped.values, marker='o', label=algo)
        
        axes[0, 0].set_xlabel('Taille du Problème')
        axes[0, 0].set_ylabel('Temps (ms)')
        axes[0, 0].set_title('Temps d\'Exécution vs Taille')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Mémoire vs Taille
        for algo in df_success['algorithm'].unique():
            data = df_success[df_success['algorithm'] == algo]
            grouped = data.groupby('problem_size')['memory_kb'].mean()
            axes[0, 1].plot(grouped.index, grouped.values, marker='o', label=algo)
        
        axes[0, 1].set_xlabel('Taille du Problème')
        axes[0, 1].set_ylabel('Mémoire (Ko)')
        axes[0, 1].set_title('Utilisation Mémoire vs Taille')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # Nœuds visités vs Taille
        for algo in df_success['algorithm'].unique():
            data = df_success[df_success['algorithm'] == algo]
            grouped = data.groupby('problem_size')['nodes_visited'].mean()
            axes[1, 0].plot(grouped.index, grouped.values, marker='o', label=algo)
        
        axes[1, 0].set_xlabel('Taille du Problème')
        axes[1, 0].set_ylabel('Nœuds Visités')
        axes[1, 0].set_title('Nœuds Visités vs Taille')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Longueur de solution vs Taille
        for algo in df_success['algorithm'].unique():
            data = df_success[df_success['algorithm'] == algo]
            grouped = data.groupby('problem_size')['solution_length'].mean()
            axes[1, 1].plot(grouped.index, grouped.values, marker='o', label=algo)
        
        axes[1, 1].set_xlabel('Taille du Problème')
        axes[1, 1].set_ylabel('Longueur de Solution')
        axes[1, 1].set_title('Longueur de Solution vs Taille')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        output_path = f'{output_dir}/size_scaling.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Longueur de solution généré: {output_path}")
        plt.close()
    
    def plot_heatmap_comparison(self, output_dir=None):
        """Heatmap des performances (temps) par algorithme et problème"""
        if output_dir is None:
            output_dir = self.output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        df_success = self.df[self.df['success']]
        
        if df_success.empty:
            return
        
        # Créer une matrice pivot
        pivot_data = df_success.pivot_table(
            values='time_ms',
            index='algorithm',
            columns='problem',
            aggfunc='mean'
        )
        
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(pivot_data, annot=True, fmt='.1f', cmap='YlOrRd', ax=ax)
        ax.set_title('Heatmap des Temps d\'Exécution (ms)')
        ax.set_xlabel('Problème')
        ax.set_ylabel('Algorithme')
        plt.tight_layout()
        
        output_path = f'{output_dir}/heatmap_time.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Heatmap des temps d'exécution généré: {output_path}")
        plt.close()
    
    def generate_all_plots(self):
        """Génère tous les graphiques"""
        print("\nGénération de tous les graphiques...")
        self.plot_time_comparison()
        self.plot_memory_comparison()
        self.plot_nodes_comparison()
        self.plot_success_rate()
        self.plot_size_scaling()
        self.plot_heatmap_comparison()
        print(f"\nTous les graphiques ont été générés dans {self.output_dir}/")


def main():
    import sys
    import glob
    
    target = 'results/benchmark_results.json'
    if len(sys.argv) > 1:
        target = sys.argv[1]
    
    print("Génération des Visualisations de Benchmarking...")
    
    # Vérifier si c'est un dossier
    target_path = Path(target)
    json_files = []
    
    if target_path.is_dir():
        # Traiter tous les fichiers JSON du dossier
        json_files = list(target_path.glob('*.json'))
        if not json_files:
            print(f"Warning: Aucun fichier JSON trouvé dans {target}")
            sys.exit(1)
        print(f"{len(json_files)} fichier(s) JSON à traiter...\n")
    elif target_path.is_file():
        json_files = [target_path]
    else:
        print(f"Error: {target} non trouvé")
        sys.exit(1)
    
    # Traiter chaque fichier JSON
    success_count = 0
    for json_file in json_files:
        try:
            print(f"\nGénération: {json_file.name}...")
            visualizer = BenchmarkVisualizer(str(json_file))
            visualizer.generate_all_plots()
            success_count += 1
        except FileNotFoundError:
            print(f"Error: {json_file} non trouvé")
        except Exception as e:
            print(f"Error lors du traitement de {json_file.name}: {e}")
    
    print(f"\n\n{success_count}/{len(json_files)} fichier(s) traité(s)")

if __name__ == '__main__':
    main()
