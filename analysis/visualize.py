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
            # Support ancien format (success: bool) et nouveau format (status: int)
            if 'status' in result:
                status = result['status']
            else:
                status = 0 if result.get('success', False) else 2
            
            row = {
                'algorithm': result['algorithm'],
                'problem': result['problem'],
                'problem_size': result['problem_size'],
                'instance_id': result['instance_id'],
                'status': status,  # 0=succès, 1=timeout, 2=pas de solution
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
        """Graphique comparatif des temps d'exécution (succès seulement, pas de timeouts)"""
        if output_dir is None:
            output_dir = self.output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # status: 0=succès, 1=timeout, 2=pas de solution
        df_success = self.df[self.df['status'] == 0]
        df_not_found = self.df[(self.df['status'] == 2) & (self.df['nodes_visited'] > 0)]
        
        if df_success.empty and df_not_found.empty:
            print("Warning: Aucun résultat à visualiser")
            return
        
        # Préparer les données pour les deux catégories (tri par problème puis algorithme)
        all_groups = sorted(
            self.df.groupby(['problem', 'algorithm']).first().index.tolist(),
            key=lambda x: (x[0], x[1])
        )
        
        # Largeur dynamique
        fig_width = self._calculate_figure_width(len(all_groups))
        fig, ax = plt.subplots(figsize=(fig_width, 8))
        
        x = np.arange(len(all_groups))
        width = 0.35
        
        # Données succès
        success_means = []
        success_stds = []
        for group in all_groups:
            data = df_success[(df_success['problem'] == group[0]) & (df_success['algorithm'] == group[1])]['time_ms']
            success_means.append(data.mean() if len(data) > 0 else 0)
            success_stds.append(data.std() if len(data) > 1 else 0)
        
        # Données "pas de solution" (pas les timeouts)
        not_found_means = []
        not_found_stds = []
        for group in all_groups:
            data = df_not_found[(df_not_found['problem'] == group[0]) & (df_not_found['algorithm'] == group[1])]['time_ms']
            not_found_means.append(data.mean() if len(data) > 0 else 0)
            not_found_stds.append(data.std() if len(data) > 1 else 0)
        
        # Barres pour les succès
        bars1 = ax.bar(x - width/2, success_means, width, yerr=success_stds, 
                       label='Succès', color='steelblue', capsize=3)
        
        # Barres pour "pas de solution" (avec hachures) - pas les timeouts
        bars2 = ax.bar(x + width/2, not_found_means, width, yerr=not_found_stds,
                       label='Pas de solution', color='lightcoral', capsize=3,
                       hatch='//', alpha=0.7, edgecolor='darkred')
        
        ax.set_xlabel('Problème - Algorithme')
        ax.set_ylabel('Temps (ms)')
        ax.set_title('Comparaison des Temps d\'Exécution (sans timeouts)')
        ax.set_xticks(x)
        ax.set_xticklabels([f"{g[0]}\n{g[1]}" for g in all_groups], rotation=45, ha='right')
        ax.legend()
        plt.tight_layout()
        
        output_path = f'{output_dir}/time_comparison.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Comparaison des temps générée: {output_path}")
        plt.close()
    
    def plot_memory_comparison(self, output_dir=None):
        """Graphique comparatif de l'utilisation mémoire (succès et pas de solution, sans timeout)"""
        if output_dir is None:
            output_dir = self.output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # status: 0=succès, 1=timeout, 2=pas de solution
        df_success = self.df[self.df['status'] == 0]
        df_not_found = self.df[(self.df['status'] == 2) & (self.df['memory_kb'] > 0)]
        
        if df_success.empty and df_not_found.empty:
            return
        
        # Tri par problème puis algorithme
        all_groups = sorted(
            self.df.groupby(['problem', 'algorithm']).first().index.tolist(),
            key=lambda x: (x[0], x[1])
        )
        
        # Largeur dynamique
        fig_width = self._calculate_figure_width(len(all_groups))
        fig, ax = plt.subplots(figsize=(fig_width, 8))
        
        x = np.arange(len(all_groups))
        width = 0.35
        
        # Mémoire - Succès
        success_mem = []
        success_std = []
        for group in all_groups:
            data = df_success[(df_success['problem'] == group[0]) & (df_success['algorithm'] == group[1])]['memory_kb']
            success_mem.append(data.mean() if len(data) > 0 else 0)
            success_std.append(data.std() if len(data) > 1 else 0)
        
        # Mémoire - Pas de solution
        not_found_mem = []
        not_found_std = []
        for group in all_groups:
            data = df_not_found[(df_not_found['problem'] == group[0]) & (df_not_found['algorithm'] == group[1])]['memory_kb']
            not_found_mem.append(data.mean() if len(data) > 0 else 0)
            not_found_std.append(data.std() if len(data) > 1 else 0)
        
        ax.bar(x - width/2, success_mem, width, yerr=success_std,
               label='Succès', color='coral', capsize=3)
        ax.bar(x + width/2, not_found_mem, width, yerr=not_found_std,
               label='Pas de solution', color='lightgray', capsize=3,
               hatch='//', alpha=0.7, edgecolor='darkred')
        
        ax.set_xlabel('Problème - Algorithme')
        ax.set_ylabel('Mémoire (Ko)')
        ax.set_title('Comparaison de l\'Utilisation Mémoire (sans timeouts)')
        ax.set_xticks(x)
        ax.set_xticklabels([f"{g[0]}\n{g[1]}" for g in all_groups], rotation=45, ha='right')
        ax.legend()
        plt.tight_layout()
        
        output_path = f'{output_dir}/memory_comparison.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Comparaison de la mémoire générée: {output_path}")
        plt.close()
    
    def _calculate_figure_width(self, num_groups):
        """Calcule la largeur optimale du graphique selon le nombre de groupes"""
        base_width = 12
        width_per_group = 1.2
        min_width = 10
        max_width = 30
        calculated = base_width + (num_groups - 5) * width_per_group
        return max(min_width, min(max_width, calculated))
    
    def plot_nodes_visited(self, output_dir=None):
        """Graphique des nœuds visités (succès et pas de solution, sans timeout)"""
        if output_dir is None:
            output_dir = self.output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # status: 0=succès, 1=timeout, 2=pas de solution
        df_success = self.df[self.df['status'] == 0]
        df_not_found = self.df[(self.df['status'] == 2) & (self.df['nodes_visited'] > 0)]
        
        if df_success.empty and df_not_found.empty:
            return
        
        # Tri par problème puis algorithme
        all_groups = sorted(
            self.df.groupby(['problem', 'algorithm']).first().index.tolist(),
            key=lambda x: (x[0], x[1])
        )
        
        # Largeur dynamique
        fig_width = self._calculate_figure_width(len(all_groups))
        fig, ax = plt.subplots(figsize=(fig_width, 8))
        
        x = np.arange(len(all_groups))
        width = 0.35
        
        # Nœuds visités - Succès
        success_visited = []
        for group in all_groups:
            data = df_success[(df_success['problem'] == group[0]) & (df_success['algorithm'] == group[1])]['nodes_visited']
            success_visited.append(data.mean() if len(data) > 0 else 0)
        
        # Nœuds visités - Pas de solution
        not_found_visited = []
        for group in all_groups:
            data = df_not_found[(df_not_found['problem'] == group[0]) & (df_not_found['algorithm'] == group[1])]['nodes_visited']
            not_found_visited.append(data.mean() if len(data) > 0 else 0)
        
        ax.bar(x - width/2, success_visited, width, label='Succès', color='steelblue')
        ax.bar(x + width/2, not_found_visited, width, label='Pas de solution', 
               color='lightcoral', hatch='//', alpha=0.7, edgecolor='darkred')
        ax.set_xlabel('Problème - Algorithme')
        ax.set_ylabel('Nombre de Nœuds')
        ax.set_title('Nœuds Visités (moyenne)')
        ax.set_xticks(x)
        ax.set_xticklabels([f"{g[0]}\n{g[1]}" for g in all_groups], rotation=45, ha='right')
        ax.legend()
        plt.tight_layout()
        
        output_path = f'{output_dir}/nodes_visited.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Nœuds visités généré: {output_path}")
        plt.close()
    
    def plot_nodes_generated(self, output_dir=None):
        """Graphique des nœuds générés (succès et pas de solution, sans timeout)"""
        if output_dir is None:
            output_dir = self.output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # status: 0=succès, 1=timeout, 2=pas de solution
        df_success = self.df[self.df['status'] == 0]
        df_not_found = self.df[(self.df['status'] == 2) & (self.df['nodes_generated'] > 0)]
        
        if df_success.empty and df_not_found.empty:
            return
        
        # Tri par problème puis algorithme
        all_groups = sorted(
            self.df.groupby(['problem', 'algorithm']).first().index.tolist(),
            key=lambda x: (x[0], x[1])
        )
        
        # Largeur dynamique
        fig_width = self._calculate_figure_width(len(all_groups))
        fig, ax = plt.subplots(figsize=(fig_width, 8))
        
        x = np.arange(len(all_groups))
        width = 0.35
        
        # Nœuds générés - Succès
        success_generated = []
        for group in all_groups:
            data = df_success[(df_success['problem'] == group[0]) & (df_success['algorithm'] == group[1])]['nodes_generated']
            success_generated.append(data.mean() if len(data) > 0 else 0)
        
        # Nœuds générés - Pas de solution
        not_found_generated = []
        for group in all_groups:
            data = df_not_found[(df_not_found['problem'] == group[0]) & (df_not_found['algorithm'] == group[1])]['nodes_generated']
            not_found_generated.append(data.mean() if len(data) > 0 else 0)
        
        ax.bar(x - width/2, success_generated, width, label='Succès', color='seagreen')
        ax.bar(x + width/2, not_found_generated, width, label='Pas de solution',
               color='lightsalmon', hatch='//', alpha=0.7, edgecolor='darkgreen')
        ax.set_xlabel('Problème - Algorithme')
        ax.set_ylabel('Nombre de Nœuds')
        ax.set_title('Nœuds Générés (moyenne)')
        ax.set_xticks(x)
        ax.set_xticklabels([f"{g[0]}\n{g[1]}" for g in all_groups], rotation=45, ha='right')
        ax.legend()
        plt.tight_layout()
        
        output_path = f'{output_dir}/nodes_generated.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Nœuds générés généré: {output_path}")
        plt.close()
    
    def plot_success_rate(self, output_dir=None):
        """Graphique du taux de succès par algorithme"""
        if output_dir is None:
            output_dir = self.output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Tri par problème puis algorithme - calculer le taux de succès (status == 0)
        success_rate = self.df.groupby(['problem', 'algorithm'], as_index=True).apply(
            lambda x: (x['status'] == 0).mean() * 100,
            include_groups=False
        )
        success_rate = success_rate.sort_index()
        
        # Largeur dynamique
        fig_width = self._calculate_figure_width(len(success_rate))
        fig, ax = plt.subplots(figsize=(fig_width, 7))
        
        success_rate.plot(kind='bar', ax=ax, color='mediumseagreen')
        ax.set_xlabel('Problème - Algorithme')
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
        
        df_success = self.df[self.df['status'] == 0]
        
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
        
        df_success = self.df[self.df['status'] == 0]
        
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
        self.plot_nodes_visited()
        self.plot_nodes_generated()
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
